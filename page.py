from quart import Blueprint, render_template, send_file, request, url_for, redirect
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

from pathlib import Path
from http.cookies import SimpleCookie
import re

page = Blueprint('Page', __name__)


class QueryPlayerData(FlaskForm):
    cookie = StringField('Cookie:', validators=[DataRequired()])
    uid = IntegerField('UID:', validators=[Length(min=9, max=9), DataRequired()])
    share_cookie = BooleanField('分享Cookie')


@page.route('/')
async def index():
    return await render_template('index.html')


@page.route('/<url_path>')
async def static_file(url_path):
    fp = Path('static') / url_path
    if fp.exists():
        return await send_file(fp)
    return redirect(
        url_for('Page.show_err_page', error_msg='Not Found', type='warning',
                desc=f'找不到 {url_path} 这个文件呢~')
    )


@page.route('/error-<string:error_msg>')
async def show_err_page(error_msg):
    error_desc = request.args.get('desc', None)
    error_type = request.args.get('type', None)
    return await render_template('error.html', error_msg=error_msg, error_type=error_type,
                                 error_description=error_desc)


@page.route('/query/user_info', methods=["GET", "POST"])
async def query_user_info():
    if request.method == 'GET':
        form = QueryPlayerData(meta={"csrf": False})
        return await render_template('user_info.html', form=form)
    form_data = await request.form
    uid: str = form_data.get('uid', None)
    cookie = SimpleCookie(form_data.get('cookie', None))
    if not re.match(r'[1256789]\d{8}', uid) or len(uid) != 9:
        return redirect(
            url_for('Page.show_err_page', error_msg='Unsupported UID format', type='danger',
                    desc='UID格式错误')
        )
    if not ('login_ticket' in cookie or
            ('account_id' and 'cookie_token') in cookie or
            ('ltuid', 'ltoken') in cookie):
        return redirect(
            url_for('Page.show_err_page', error_msg='Invalid Cookie format', type='danger',
                    desc='Cookie格式错误')
        )
    
