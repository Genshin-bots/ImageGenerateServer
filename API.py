from flask import Blueprint, request, url_for, render_template, send_file
from style import Style, DEFAULT_STYLE
from PIL import Image

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
def get_images(filename):
    file_path = Path('tmp_images') / filename
    if not file_path.exists():
        return {
            "retcode": 4,
            "ErrorMsg": f"File {filename} not found"
        }
    return send_file(file_path)


@api.route('/generator/user_info', methods=['GET', 'POST'])
async def gen_info_card():
    if request.method == 'POST':
        args: dict = dict(request.args)
        try:
            data = json.loads(request.data)
        except json.decoder.JSONDecodeError as err:
            return {
                "retcode": 2,
                "ErrorMsg": str(err)
            }
        cur_style = args.get("style") if "style" in args else DEFAULT_STYLE
        if cur_style not in style.styles:
            return {
                "retcode": 3,
                "ErrorMsg": f"Style {cur_style} not found."
            }
        try:
            generated = await style.user_info(cur_style, data, **args)
        except KeyError:
            return {
                "retcode": 2,
                "ErrorMsg": "Data is not in standard format"
            }
        pic_type = args.get("type").lower() if "type" in args else 'png'
        filename = time.strftime('%Y%m%d%H%M%S-' + ''.join(random.choices(abcs, k=8)) + '.' + pic_type)
        filepath = SAVE_PATH / filename
        quality = args.get("quality") if "quality" in args else 100
        if isinstance(generated, Image.Image):
            try:
                generated.save(filepath, quality=quality)
            except ValueError as err_msg:
                return {
                    "retcode": 2,
                    "ErrorMsg": str(err_msg)
                }
            return {
                "retcode": 0,
                "Image_url": url_for('.get_images', filename=filename)
            }
        if isinstance(generated, bytes):
            with open(filepath, 'rb') as f:
                f.write(generated)
            return {
                "retcode": 0,
                "Image_url": url_for('.get_images', filename=filename)
            }
        if isinstance(generated, str):
            return {
                "retcode": 0,
                "text": generated
            }
        return {
            "retcode": 0,
            "data": str(generated)
        }

    return render_template('index.html')
