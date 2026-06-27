# -*- coding: utf-8 -*-
"""
知了标讯 - 爬虫 GUI
依赖: pip install DrissionPage openpyxl
启动前手动打开浏览器调试端口: chrome.exe --remote-debugging-port=9333
"""

import os
import sys
import csv
import time
import random
import shutil
import logging
import threading
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

from DrissionPage import Chromium, ChromiumPage, SessionPage

# ==================== 配置 ====================
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "crawler_config.json"
LOG_FILE = BASE_DIR / "crawler.log"
MAX_LOG_LINES = 3000

HEADERS = ["标题", "招标公司", "中标公司", "金额", "公告日期", "地区"]

# 默认配置
DEFAULT_CONFIG = {
    "save_dir": str(BASE_DIR / "data"),
    "filename": "bid_info",
    "max_pages": 300,
    "wait_min": 1.0,
    "wait_max": 3.0,
}


# ==================== 日志工具 ====================
class LogHandler(logging.Handler):
    """日志处理器：同时输出到 GUI Text 控件和文件"""

    def __init__(self, text_widget=None):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # 写入 GUI
        if self.text_widget:
            self.text_widget.after(0, lambda: self._append_to_widget(msg))
        # 写入文件
        self._write_to_file(msg)

    def _append_to_widget(self, msg):
        try:
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
        except Exception:
            pass

    def _write_to_file(self, msg):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
            # 保留最新 3000 行
            _trim_log_file()
        except Exception:
            pass


def _trim_log_file():
    """裁剪日志文件，保留最新 MAX_LOG_LINES 行"""
    try:
        if not LOG_FILE.exists():
            return
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > MAX_LOG_LINES:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-MAX_LOG_LINES:])
    except Exception:
        pass


def setup_logger(text_widget=None):
    """初始化日志器"""
    logger = logging.getLogger("crawler")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = LogHandler(text_widget)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                                            datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    return logger


# ==================== CSV / Excel 工具 ====================
def get_csv_path(save_dir, filename):
    """获取 csv 文件路径"""
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    return save_path / f"{filename}.csv"


def backup_csv(csv_path):
    """备份 csv 到 backup.csv"""
    if csv_path.exists():
        backup_path = csv_path.with_name(csv_path.stem + "_backup.csv")
        shutil.copy2(csv_path, backup_path)
        return backup_path
    return None


def csv_to_excel(csv_path, excel_path):
    """将 csv 导出为 xlsx，带表头"""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "标讯数据"

    # 写表头
    # ws.append(HEADERS)

    # 写数据
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    # 调整列宽
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                max_len = max(max_len, len(str(cell.value or "")))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len * 2 + 4, 50)

    wb.save(excel_path)


# ==================== 反爬工具 ====================
class AntiCrawl:
    """反爬绕过机制"""

    @staticmethod
    def random_delay(min_sec=1.0, max_sec=3.0):
        """随机等待"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    @staticmethod
    def human_scroll(page):
        """模拟人类滚动行为"""
        try:
            total = page.run_js("return document.body.scrollHeight")
            if not total:
                return
            total = int(total)
            for _ in range(random.randint(1, 3)):
                pos = random.randint(100, max(200, total // 3))
                page.run_js(f"window.scrollTo(0, {pos})")
                time.sleep(random.uniform(0.2, 0.6))
            page.scroll.to_bottom()
            time.sleep(random.uniform(0.3, 0.8))
        except Exception:
            pass

    @staticmethod
    def random_mouse_move(page):
        """随机鼠标移动"""
        try:
            eles = page.eles("tag:a") or page.eles("tag:p") or page.eles("tag:span")
            if eles:
                target = random.choice(eles[: min(len(eles), 5)])
                page.actions.move_to(target)
                time.sleep(random.uniform(0.1, 0.4))
        except Exception:
            pass

    @staticmethod
    def random_scroll_edge(page):
        """随机滚动页面边缘区域"""
        try:
            page.scroll.to_half()
            time.sleep(random.uniform(0.3, 0.7))
        except Exception:
            pass


# ==================== 爬虫引擎 ====================
class CrawlerEngine:
    """爬虫核心引擎（在子线程中运行）"""

    def __init__(self, config, logger, browser, on_data, on_done):
        self.config = config
        self.log = logger
        self.browser = browser      # 复用 GUI 已连接的浏览器
        self.on_data = on_data      # 回调: (row_dict) -> None
        self.on_done = on_done      # 回调: (total_pages, total_items, elapsed) -> None
        self._stop_flag = threading.Event()
        self.http = SessionPage()   # 用于发 HTTP 请求获取详情，不走浏览器加速

    def stop(self):
        self._stop_flag.set()

    def run(self):
        total_pages = 0
        total_items = 0
        start_time = time.time()
        csv_path = get_csv_path(self.config["save_dir"], self.config["filename"])

        # 备份
        backup = backup_csv(csv_path)
        if backup:
            self.log.info(f"已备份: {backup.name}")

        try:
            page = self.browser.latest_tab
            self.log.info(f"已连接: {page.title}")

            while not self._stop_flag.is_set():
                total_pages += 1

                # 反爬：滚动、鼠标移动
                AntiCrawl.random_scroll_edge(page)
                AntiCrawl.random_mouse_move(page)

                items = page.eles(".bidWrap")
                self.log.info(f"第 {total_pages} 页，发现 {len(items)} 条")

                if not items:
                    self.log.warning("未找到数据项，可能页面结构变化")
                    break

                for item in items:
                    if self._stop_flag.is_set():
                        break
                    try:
                        row = {}
                        row["标题"] = item.ele("tag:h3").text
                        gs = item.ele(".companyinfo")
                        gs_list = gs.eles("tag:p")
                        row["招标公司"] = gs_list[1].text if len(gs_list) > 1 else ""
                        cnt = len(gs_list)
                        row["中标公司"] = gs_list[3].text if cnt >= 4 else "无"
                        row["金额"] = item.ele(".brandInfo-money").text
                        row["公告日期"] = item.ele(".brandInfo-date").text
                        row["地区"] = item.ele(".brandInfo-area").text
                        if cnt >= 5 and (gs_list[4].text).startswith("+"):
                            # 用 SessionPage 发 HTTP 请求，不用开新标签页，大幅提速
                            try:
                                bid_ele = item.ele('.biditem')
                                bidding_id = bid_ele.attr('bid')
                                url = f"https://www.zhiliaobiaoxun.com/content/{bidding_id}/b2"
                                resp = self.http.get(url)
                                companies = resp.eles(".bidCompany")[1:]
                                row["中标公司"] = ", ".join([c.text for c in companies])
                            except Exception as e:
                                self.log.warning(f"获取多个中标公司失败: {e}")

                                                       
                        # 写入 csv（追加）
                        with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
                            writer = csv.writer(f)
                            writer.writerow([row[h] for h in HEADERS])

                        total_items += 1
                        self.on_data(row)

                    except Exception as e:
                        self.log.warning(f"解析条目失败: {e}")
                        continue

                # 检查最大页数
                if total_pages >= self.config["max_pages"]:
                    self.log.info(f"已达到最大页数: {self.config['max_pages']}")
                    break

                # 翻页
                try:
                    next_btn = page.ele(".btn-next")
                    if next_btn and "disabled" not in (next_btn.attr("class") or ""):
                        next_btn.click()
                        AntiCrawl.random_delay(
                            self.config["wait_min"],
                            self.config["wait_max"],
                        )
                    else:
                        self.log.info("已到最后一页")
                        break
                except Exception:
                    self.log.warning("翻页失败，可能已到最后一页")
                    break

        except Exception as e:
            self.log.error(f"爬取异常: {e}")
        finally:
            elapsed = time.time() - start_time
            self.on_done(total_pages, total_items, elapsed)


# ==================== GUI ====================
class CrawlerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("知了标讯爬虫")
        self.root.geometry("750x650")
        self.root.minsize(600, 500)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.engine = None
        self.engine_thread = None
        self.running = False
        self.total_count = 0

        self._load_config()
        self._build_ui()
        self._init_logger()
        self._init_browser()

    # ---------- 配置 ----------
    def _load_config(self):
        import json
        try:
            if CONFIG_FILE.exists():
                self.config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            else:
                self.config = DEFAULT_CONFIG.copy()
        except Exception:
            self.config = DEFAULT_CONFIG.copy()

    def _save_config(self):
        import json
        try:
            CONFIG_FILE.write_text(
                json.dumps(self.config, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------- 浏览器 ----------
    def _init_browser(self):
        """初始化：仅连接浏览器，不开始爬取"""
        try:
            self.browser = Chromium("127.0.0.1:9333")
            self.log.info("浏览器已连接，等待操作...")
        except Exception as e:
            messagebox.showwarning("警告", f"无法连接浏览器调试端口(9333):\n{e}\n\n请先启动:\nchrome.exe --remote-debugging-port=9333")
            self.browser = None

    # ---------- 日志 ----------
    def _init_logger(self):
        self.log = setup_logger(self.log_text)

    # ---------- UI ----------
    def _build_ui(self):
        # -- 设置区 --
        frm_setting = ttk.LabelFrame(self.root, text="设置", padding=8)
        frm_setting.pack(fill=tk.X, padx=8, pady=(8, 4))

        row0 = ttk.Frame(frm_setting)
        row0.pack(fill=tk.X, pady=2)
        ttk.Label(row0, text="存储目录:").pack(side=tk.LEFT)
        self.entry_dir = ttk.Entry(row0, width=40)
        self.entry_dir.insert(0, self.config["save_dir"])
        self.entry_dir.pack(side=tk.LEFT, padx=4)
        ttk.Button(row0, text="浏览", width=6, command=self._browse_dir).pack(side=tk.LEFT)

        row1 = ttk.Frame(frm_setting)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="文件名前缀:").pack(side=tk.LEFT)
        self.entry_filename = ttk.Entry(row1, width=20)
        self.entry_filename.insert(0, self.config["filename"])
        self.entry_filename.pack(side=tk.LEFT, padx=4)

        ttk.Label(row1, text="  最大页数:").pack(side=tk.LEFT)
        self.entry_max_pages = ttk.Entry(row1, width=6)
        self.entry_max_pages.insert(0, str(self.config["max_pages"]))
        self.entry_max_pages.pack(side=tk.LEFT, padx=4)

        row2 = ttk.Frame(frm_setting)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="翻页等待(秒):").pack(side=tk.LEFT)
        self.entry_wait_min = ttk.Entry(row2, width=5)
        self.entry_wait_min.insert(0, str(self.config["wait_min"]))
        self.entry_wait_min.pack(side=tk.LEFT, padx=2)

        ttk.Label(row2, text=" ~ ").pack(side=tk.LEFT)
        self.entry_wait_max = ttk.Entry(row2, width=5)
        self.entry_wait_max.insert(0, str(self.config["wait_max"]))
        self.entry_wait_max.pack(side=tk.LEFT, padx=2)

        ttk.Button(row2, text="保存设置", command=self._save_settings).pack(side=tk.LEFT, padx=20)

        # -- 按钮区 --
        frm_btn = ttk.Frame(self.root)
        frm_btn.pack(fill=tk.X, padx=8, pady=4)

        self.btn_start = ttk.Button(frm_btn, text="▶ 开始爬取", command=self._start_crawl, width=14)
        self.btn_start.pack(side=tk.LEFT, padx=4)

        self.btn_stop = ttk.Button(frm_btn, text="■ 停止", command=self._stop_crawl, state=tk.DISABLED, width=10)
        self.btn_stop.pack(side=tk.LEFT, padx=4)

        self.btn_export = ttk.Button(frm_btn, text="导出 Excel", command=self._export_excel, width=12)
        self.btn_export.pack(side=tk.LEFT, padx=4)

        self.lbl_status = ttk.Label(frm_btn, text="就绪", foreground="gray")
        self.lbl_status.pack(side=tk.RIGHT, padx=4)

        # -- 统计区 --
        frm_stat = ttk.Frame(self.root)
        frm_stat.pack(fill=tk.X, padx=8)
        self.lbl_stat = ttk.Label(frm_stat, text="已爬取: 0 条 | 0 页 | 耗时: --")
        self.lbl_stat.pack(side=tk.LEFT)

        # -- 日志区 --
        frm_log = ttk.LabelFrame(self.root, text="日志", padding=4)
        frm_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.log_text = scrolledtext.ScrolledText(
            frm_log, wrap=tk.WORD, state=tk.NORMAL,
            font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.config["save_dir"])
        if path:
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, path)

    def _save_settings(self):
        try:
            self.config["save_dir"] = self.entry_dir.get()
            self.config["filename"] = self.entry_filename.get()
            self.config["max_pages"] = int(self.entry_max_pages.get())
            self.config["wait_min"] = float(self.entry_wait_min.get())
            self.config["wait_max"] = float(self.entry_wait_max.get())
            self._save_config()
            messagebox.showinfo("提示", "设置已保存")
        except ValueError:
            messagebox.showerror("错误", "参数格式不正确")

    # ---------- 爬虫控制 ----------
    def _start_crawl(self):
        if self.running:
            return

        if not self.browser:
            try:
                self._init_browser()
            except Exception:
                return

        if not self.browser:
            return

        # 读取最新设置
        self.config["save_dir"] = self.entry_dir.get()
        self.config["filename"] = self.entry_filename.get()
        try:
            self.config["max_pages"] = int(self.entry_max_pages.get())
            self.config["wait_min"] = float(self.entry_wait_min.get())
            self.config["wait_max"] = float(self.entry_wait_max.get())
        except ValueError:
            pass

        self.running = True
        self.total_count = 0
        self._start_time = time.time()

        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="运行中...", foreground="green")

        # 确保目录存在，写入 csv 表头（如果文件不存在）
        csv_path = get_csv_path(self.config["save_dir"], self.config["filename"])
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        if not csv_path.exists():
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerow(HEADERS)

        # 启动爬虫线程
        self.engine = CrawlerEngine(
            config=self.config,
            logger=self.log,
            browser=self.browser,
            on_data=self._on_data,
            on_done=self._on_done,
        )
        self.engine_thread = threading.Thread(target=self.engine.run, daemon=True)
        self.engine_thread.start()

    def _stop_crawl(self):
        if self.engine:
            self.engine.stop()
        self.running = False
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="停止中...", foreground="orange")
        self.log.info("用户点击停止，等待当前操作完成...")

    def _on_data(self, row):
        """每获取一条数据回调（在子线程调用，通过 after 更新 UI）"""
        self.total_count += 1
        elapsed = time.time() - self._start_time
        self.root.after(0, lambda: self.lbl_stat.config(
            text=f"已爬取: {self.total_count} 条 | 耗时: {elapsed:.0f}秒"
        ))

    def _on_done(self, total_pages, total_items, elapsed):
        """爬取结束回调"""
        self.running = False
        self.root.after(0, lambda: self._finish(total_pages, total_items, elapsed))

    def _finish(self, total_pages, total_items, elapsed):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="就绪", foreground="gray")
        self.lbl_stat.config(
            text=f"完成！爬取 {total_pages} 页，共 {total_items} 条，耗时 {elapsed:.0f}秒"
        )
        self.log.info(f"爬取结束: {total_pages} 页, {total_items} 条, 耗时 {elapsed:.1f}秒")

    # ---------- 导出 Excel ----------
    def _export_excel(self):
        csv_path = get_csv_path(self.config["save_dir"], self.config["filename"])
        if not csv_path.exists():
            messagebox.showwarning("提示", "CSV 文件不存在，请先爬取数据")
            return

        excel_path = csv_path.with_suffix(".xlsx")
        try:
            csv_to_excel(csv_path, excel_path)
            messagebox.showinfo("成功", f"已导出到:\n{excel_path}")
            self.log.info(f"Excel 导出成功: {excel_path.name}")
        except ImportError:
            messagebox.showerror("错误", "缺少 openpyxl 库，请执行:\npip install openpyxl")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def _on_close(self):
        """关闭窗口时停止爬虫"""
        if self.running and self.engine:
            self.engine.stop()
        self._save_config()
        self.root.destroy()

    # ---------- 启动 ----------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CrawlerGUI()
    app.run()
