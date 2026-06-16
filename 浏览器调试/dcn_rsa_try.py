MODULUS_HEX = "be44aec4d73408f6b60e6fe9e3dc55d0e1dc53a1e171e071b547e2e8e0b7da01c56e8c9bcf0521568eb111adccef4e40124b76e33e7ad75607c227af8f8e0b759c30ef283be8ab17a84b19a051df5f94c07e6e7be5f77866376322aac944f45f3ab532bb6efc70c1efa524d821d16cafb580c5a901f0defddea3692a4e68e6cd"
PUBLIC_EXPONENT_HEX = "10001"


def legacy_chunk_size(modulus_hex: str) -> int:
    # Match RSA.js: chunkSize = 2 * biHighIndex(modulus)
    digit_count_base_65536 = (len(modulus_hex) + 3) // 4
    return 2 * (digit_count_base_65536 - 1)


def encode_ohdave_block(text: str, chunk_size: int) -> int:
    raw = bytearray()
    for ch in text:
        code = ord(ch)
        if code > 0xFF:
            raise ValueError("legacy RSA.js path only supports code points <= 255")
        raw.append(code)

    if len(raw) > chunk_size:
        raise ValueError(f"plaintext too long for single block: {len(raw)} > {chunk_size}")

    raw.extend(b"\x00" * (chunk_size - len(raw)))
    return int.from_bytes(raw, byteorder="little", signed=False)


def dcn_rsa_encrypt(password: str) -> str:
    modulus = int(MODULUS_HEX, 16)
    exponent = int(PUBLIC_EXPONENT_HEX, 16)
    chunk_size = legacy_chunk_size(MODULUS_HEX)
    block = encode_ohdave_block(password, chunk_size)
    encrypted = pow(block, exponent, modulus)
    return format(encrypted, "x")


if __name__ == "__main__":
    import json
    import sys

    password = sys.argv[1] if len(sys.argv) > 1 else "123456"
    encrypted = dcn_rsa_encrypt(password)
    print(json.dumps({"password": password, "encrypted": encrypted}, ensure_ascii=False, indent=2))
