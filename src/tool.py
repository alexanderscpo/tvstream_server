import json

from pathlib import Path
from typing import Tuple

from settings import M3U8_DIR, JSON_DIR, PUBLIC_M3U8_DIR, ADDRESS

def m3u8_to_json(file_path: Path) -> Path:
    name = file_path.stem
    tv_json: dict = {'user-agent': '', 'channels': []}

    with open(file_path, mode='+r', encoding='utf-8') as m3u8_file:
        i: int = 0
        missing_url = False
        missing_user_agent = True

        for line in m3u8_file.readlines():
            if line == '#EXTM3U' or line[0] == 10:
                continue

            elif line.startswith('#EXTINF:-1') and not missing_url:
                i += 1
                missing_url = True
                canal_name = line.split(',')[1]
                canal_name = canal_name.rstrip()
                tv_json['channels'].append({i: {'name': canal_name, 'url': ''}})

            elif line.startswith('http') and missing_url:
                if '|' in line:
                    url, user_agent = line.split('|')
                    user_agent = user_agent.split('=')[1].rstrip()
                else:
                    url = line
                    user_agent = ''
                if missing_user_agent:
                    tv_json['user-agent'] = user_agent
                    missing_user_agent = False
                tv_json['channels'][i - 1][i]['url'] = url
                missing_url = False

    json_m3u8 = JSON_DIR / f'{name}.json'

    with open(json_m3u8, 'w+', encoding='utf-8') as file_json:
        json.dump(tv_json, file_json, indent=4)

    return json_m3u8


def json_to_m3u8(file_path: Path):
    name_tv = file_path.stem
    new_m3u8 = PUBLIC_M3U8_DIR / f'{name_tv}.m3u8'
    hostname = f'{ADDRESS[0]}:{ADDRESS[1]}'
    
    with open(file_path, mode='+r', encoding='utf-8') as json_file:
        tv_json: dict = json.load(json_file)
        
        with open(new_m3u8, mode='w+', encoding='utf-8') as m3u8_file:
            m3u8_file.write('#EXTM3U\n')
            for i, channel in enumerate(tv_json['channels']):
                name = channel[str(i + 1)]['name']
                m3u8_file.write(f'#EXTINF:-1", {name}\n')
                m3u8_file.write(f'http://{hostname}/tv/{name_tv}/channel/{i + 1}\n\n')


def loads_m3u8():
    hostname = f'{ADDRESS[0]}:{ADDRESS[1]}'
    
    for file in M3U8_DIR.iterdir():
        if file.suffix == '.m3u8':
            new_json = m3u8_to_json(file)
            json_to_m3u8(new_json)
            

def get_url_channel(tv_id: str, channel_id: str) -> Tuple[str, str]:
    file = JSON_DIR / f'{tv_id}.json'
    
    with open(file, mode='r', encoding='utf-8') as file:
        tv_json = json.load(file)
        for channel in tv_json['channels']:
            if channel_id in channel:
                return channel[channel_id]['url'], tv_json['user-agent']

    return '', ''
