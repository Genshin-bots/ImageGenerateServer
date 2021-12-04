import requests

from pathlib import Path
import json

with open(Path(__file__).parent / "user_info.json", 'r', encoding='utf-8') as f:
    user_info = json.load(f)

if __name__ == '__main__':
    print(requests.post('http://127.0.0.1:5000/generator/user_info', json=user_info, params={
        # "style": "egenshin",
        # "uid": 800505056,
        # "qid": 10001,
        "bg_url": "https://img0.baidu.com/it/u=628426564,2176264072&fm=26&fmt=auto"
    }).text)
