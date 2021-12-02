# -*- coding: UTF-8 -*-
from sqlitedict import SqliteDict
from PIL import ImageFont
import aiofiles
import httpx
import yaml

import os
import re
import time
import json
import base64
import datetime
import functools
from io import BytesIO
from pathlib import Path


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dict_obj):
    if not isinstance(dict_obj, dict):
        return dict_obj
    inst = Dict()
    for k, v in dict_obj.items():
        inst[k] = dict_to_object(v)
    return inst


# 获取配置
def get_config(name='config.yml'):
    file = open(os.path.join(os.path.dirname(__file__), str(Path(name))),
                'r',
                encoding="utf-8")
    return dict_to_object(yaml.load(file.read(), Loader=yaml.FullLoader))


config = get_config()


# 获取字符串中的关键字
def get_msg_keyword(keyword, msg, is_first=False):
    msg = msg[0] if isinstance(msg, tuple) else msg
    res = re.split(format_reg(keyword, is_first), msg, 1)
    res = tuple(res[::-1]) if len(res) == 2 else False
    return ''.join(res) if is_first and res else res


# 格式化配置中的正则表达式
def format_reg(keyword, is_first=False):
    keyword = keyword if isinstance(keyword, list) else [keyword]
    return f"{'|'.join([f'^{i}' for i in keyword] if is_first else keyword)}"


def get_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


db = {}


# 初始化数据库
def init_db(db_dir, db_name='db.sqlite', tablename='unnamed') -> SqliteDict:
    if db.get(db_name):
        return db[db_name]
    db[db_name] = SqliteDict(get_path(db_dir, db_name),
                             tablename=tablename,
                             encode=json.dumps,
                             decode=json.loads,
                             autocommit=True)
    return db[db_name]


# 寻找MessageSegment里的某个关键字的位置
def find_ms_str_index(ms, keyword, is_first=False):
    for index, item in enumerate(ms):
        if item['type'] == 'text' and re.search(format_reg(keyword, is_first),
                                                item['data']['text']):
            return index
    return -1


def filter_list(plist, func):
    return list(filter(func, plist))


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def get_next_day():
    return time.mktime((datetime.date.today() +
                        datetime.timedelta(days=+1)).timetuple()) + 1000


def get_font(size, w='85'):
    return ImageFont.truetype(get_path('assets', 'font', f'HYWenHei {w}W.ttf'),
                              size=size)


def pil2b64(data):
    bio = BytesIO()
    data = data.convert("RGB")
    data.save(bio, format='JPEG', quality=80)
    base64_str = base64.b64encode(bio.getvalue()).decode()
    return 'base64://' + base64_str


def cache(ttl=datetime.timedelta(hours=1), arg_key=None):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            default_data = {"time": None, "value": None}
            ins_key = 'default'
            if arg_key:
                ins_key = arg_key + str(kw.get(arg_key, ''))
                data = cache_data.get(ins_key, default_data)
            else:
                data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data['time'] or now - data['time'] > ttl:
                try:
                    data['value'] = await func(*args, **kw)
                    data['time'] = now
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data['value']

        return wrapped

    return wrap


async def github(path):
    try:
        url = f'https://cdn.jsdelivr.net/gh/{path}'
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
        return await res.content
    except httpx.ConnectError:
        raise


gh_end_point = 'pcrbot/erinilis-modules/egenshin/'


async def gh_json(file_path):
    return json.loads(await github(gh_end_point + file_path), object_hook=Dict)


async def gh_file(file_path, **kw):
    kw['url'] = gh_end_point + file_path
    return await require_file(**kw)


async def require_file(file=None,
                       r_mode='rb',
                       encoding=None,
                       url=None,
                       use_cache=True,
                       w_mode='wb',
                       timeout=30):
    async def read():
        async with aiofiles.open(file, r_mode, encoding=encoding) as fp:
            return await fp.read()

    if not any([file, url]):
        raise ValueError('file or url not null')

    file = file and Path(file)

    if file and file.exists() and use_cache:
        return await read()

    if not url:
        raise ValueError('url not null')

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=timeout)
        content = await res.content
    except httpx.ConnectError:
        raise

    if file:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, w_mode) as f:
            f.write(content)
    return await read()


@cache(ttl=datetime.timedelta(minutes=30), arg_key='url')
async def cache_request_json(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10)
    return await res.json(object_hook=Dict)


@cache(ttl=datetime.timedelta(hours=24))
async def get_game_version():
    url = 'https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource?key=eYd89JmJ&launcher_id=18'
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10)
    json_data = await res.json(object_hook=Dict)
    if json_data.retcode != 0:
        raise Exception(json_data.message)
    latest = json_data.data.game.latest
    return latest.version


running = {}


class process:
    def __init__(self, key, timeout=0):
        self.key = key
        self.timeout = timeout

    def get(self):
        return running.get(self.key, {})

    def start(self):
        running[self.key] = {'run': True, 'start_time': time.time()}
        return self

    def ok(self):
        if running.get(self.key):
            del running[self.key]

    def is_run(self):
        run = self.get()
        if not run:
            return False
        if run.get('start_time') + self.timeout < time.time(
        ) and not self.timeout == 0:
            self.ok()
            return False
        return bool(run.get('run'))