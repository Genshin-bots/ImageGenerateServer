from quart import Blueprint, request, url_for, send_file, render_template
from style import Style, DEFAULT_STYLE
import data_response as response
from PIL import Image
import aiofiles

from pathlib import Path
from string import ascii_letters
import random
import time
import json

SAVE_PATH = Path('tmp_images')

style = Style()
api = Blueprint('API', __name__)
abcs = ascii_letters + '0123456789'

if not SAVE_PATH.exists():
    SAVE_PATH.mkdir()


@api.route('/image/<string:filename>')
async def get_images(filename):
    file_path = Path('tmp_images') / filename
    if not file_path.exists():
        return response.not_found(filename)
    return await send_file(file_path)


@api.route('/generator/user_info', methods=['GET', 'POST'])
async def gen_info_card():
    if request.method == 'POST':
        args: dict = dict(request.args)
        try:
            data = json.loads(request.data)
        except json.decoder.JSONDecodeError as err:
            return response.data_error(err)
        cur_style = args.get("style") if "style" in args else DEFAULT_STYLE
        if cur_style not in style.styles:
            return response.style_err(cur_style)
        try:
            generated = (await style.user_info(cur_style, data, **args)).convert('RGB')
        except KeyError:
            return response.data_error("Data is not in standard format")
        pic_type = args.get("type").lower() if "type" in args else 'jpg'
        filename = time.strftime('%Y%m%d%H%M%S-' + ''.join(random.choices(abcs, k=8)) + '.' + pic_type)
        filepath = SAVE_PATH / filename
        quality = args.get("quality") if "quality" in args else 100
        if isinstance(generated, Image.Image):
            try:
                generated.save(filepath, quality=quality)
            except Exception as err:
                if str(err) == 'Invalid quality setting':
                    generated.save(filepath)
                else:
                    return response.generator_error(err)
            return response.success(url_for('.get_images', filename=filename))
        if isinstance(generated, bytes):
            async with aiofiles.open(filepath, 'rb') as f:
                await f.write(generated)
            return response.success(url_for('.get_images', filename=filename))
        if isinstance(generated, str):
            return response.success(generated, "Text")
        return response.success(generated, "Data")
    if request.method == 'GET':
        return await render_template('user_info.html')
