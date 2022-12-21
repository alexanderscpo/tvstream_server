from pathlib import Path

ADDRESS = ('localhost', 3210)

BASE_DIR = Path(__file__).resolve().parent

JSON_DIR = BASE_DIR / 'list_json'

M3U8_DIR = BASE_DIR / 'list_m3u8'

TEMP_DIR = BASE_DIR / 'temp'

PUBLIC_M3U8_DIR = BASE_DIR / 'public_m3u8'
