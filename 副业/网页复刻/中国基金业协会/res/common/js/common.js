/*ipad适应*/
function orient() {
    if (window.screen.width > 640) {
        var viewport = document.querySelector("meta[name=viewport]"); //获取meta对象的第一种方法	
        if (window.orientation == 90 || window.orientation == -90) {
            //ipad、iphone竖屏；Andriod横屏
            $("body").attr("class", "landscape");
            orientation = 'landscape';
            var phoneWidth = parseInt(window.screen.width),
                phoneScale = 1000 / 1300,
                ua = navigator.userAgent;
        } else if (window.orientation == 0 || window.orientation == 180) {
            //ipad、iphone横屏；Andriod竖屏
            $("body").attr("class", "portrait");
            orientation = 'portrait';
            var phoneWidth = parseInt(window.screen.width),
                phoneScale = 768 / 1300,
                ua = navigator.userAgent;
        }
        if (viewport && phoneScale) {
            viewport.setAttribute('content', 'width=1024 maximum-scale =' + phoneScale + ', minimum-scale=' + phoneScale + ', initial-scale = ' + phoneScale + '');
        }
    }
}
$(function() {
    //页面加载时调用
    $(function() {
        orient();
    });
    //用户变化屏幕方向时调用
    $(window).bind('orientationchange', function(e) {
        orient();
    });
    /*底部网站导航*/
    $(".map-site span").click(function() {
        $(".site-nav").slideToggle();
        $('html,body').animate({
            scrollTop: $('.mod-copy').offset().top
        }, 1000);
        $(this).parent().toggleClass("map-unfold");
    });
    /*底部网站浏览量*/
    $.ajax({
        url: "/amac-infodisc/api/hits/pagecount?random=" + Math.random(),
        type: "get",
        data: {},
        success: function(data) {
            if (data.pageCount) {
                $("#clickCount").html("浏览量：" + data.pageCount);
            }
        }
    });
})