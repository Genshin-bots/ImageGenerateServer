from quart import Quart, render_template, send_file
from data_response import not_found
from API import api

from pathlib import Path

config = {
    'TEMPLATES_AUTO_RELOAD': True,  # 当模板被改变的时候自动重载
    'JSON_SORT_KEYS': False,  # 整理返回JSON的键
    'JSON_AS_ASCII': False,  # 将JSON内的字符转换为ASCII
    # 'CACHE_TYPE': 'SimpleCache'  # 缓存类型 更多查阅https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching
}

app = Quart(__name__)
app.config.from_mapping(config)
app.register_blueprint(api)


@app.route('/')
async def index(url_path=None):
    return await render_template('index.html')


@app.route('/<url_path>')
async def static_file(url_path):
    fp = Path('static') / url_path
    if fp.exists():
        return await send_file(fp)
    return not_found(url_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
