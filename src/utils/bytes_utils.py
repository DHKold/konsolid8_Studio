def bytes_to_hex(data: bytes, groupsize: int = 0, linesize: int=0) -> str:
    """Convert binary data to a hexadecimal string."""
    hex_str = data.hex()
    if groupsize > 0:
        hex_str = " ".join(hex_str[i:i + groupsize] for i in range(0, len(hex_str), groupsize))
    return hex_str.upper()

def bytes_to_python(data: bytes) -> str:
    """Convert binary data to a Python byte string."""
    return "b'" + data.hex() + "'"