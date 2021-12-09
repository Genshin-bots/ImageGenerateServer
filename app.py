from quart import Quart, render_template
from API import api

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
async def index():
    return await render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
