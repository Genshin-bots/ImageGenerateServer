from PIL import Image, ImageFont, ImageFilter, ImageDraw, ImageEnhance
import httpx
import toml

from io import BytesIO
from time import time
from pathlib import Path

config = toml.load(Path(__file__).parent / "config.toml")
ASSETS = Path(__file__).parent / "assets"
AVATARS = Path(__file__).parent.parent / "avatars"
head_bg: Image.Image = Image.open(ASSETS / "uid-upper-v2-2.png")
middle_bg: Image.Image = Image.open(ASSETS / "card-middle.png")
footer_bg: Image.Image = Image.open(ASSETS / "card-bottom.png")
character_card_bg: Image.Image = Image.open(ASSETS / "character_card_bg.png")
avatar_bg: Image.Image = Image.open(ASSETS / "avatar.png")
character_card_rgb = {}

font_character_card = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=16)
font_stats = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=32)

for c in config["Colors"]:
    element_color = config["Colors"][c] if config["Colors"][c] != "" else None
    tmp_bg = Image.new('RGBA', (160, 220), None)
    tmp_bg.paste(Image.new('RGBA', (160, 220), color=element_color), mask=character_card_bg.split()[3])
    character_card_rgb[c] = tmp_bg


async def get_avatar(url) -> Image.Image:
    filename = url.split('/')[-1:][0]
    file_path = AVATARS / filename
    if file_path.exists():
        return Image.open(file_path)
    async with httpx.AsyncClient() as c:
        resp = await c.get(url)
        if resp.status_code != 200:
            raise httpx.RequestError
    with open(file_path, 'wb+') as f:
        f.write(resp.content)
    return Image.open(file_path)


async def user_info(data, **kwargs):
    t2 = time()
    uid = kwargs.get('uid') if 'uid' in kwargs else None
    nickname = kwargs.get('nickname') if 'nickname' in kwargs else None
    avatar = kwargs.get('avatar') if 'avatar' in kwargs else None

    data_characters = data["data"]["avatars"]
    data_stats = data["data"]["stats"]
    # 计算
    character_amount = len(data_characters)
    cols = character_amount // 7 if character_amount % 7 == 0 else character_amount // 7 + 1
    canvas_height = head_bg.size[1] + cols * middle_bg.size[1] + footer_bg.size[1]
    # 三画布：底、中、上
    canvas = Image.new('RGBA', (middle_bg.size[0], canvas_height), None)
    character_bg_canvas = canvas.copy()
    character_front = canvas.copy()

    f_draw = ImageDraw.Draw(character_front)
    canvas.paste(head_bg)
    canvas.paste(footer_bg, (0, canvas_height - footer_bg.size[1]))

    # 顶部
    if avatar:
        if avatar.isdigit():
            async with httpx.AsyncClient() as client:
                avatar_im = avatar_bg.copy()
                resp = await client.get(f'https://q.qlogo.cn/headimg_dl?dst_uin={avatar}&spec=640&img_type=jpg')
                tmp_im = Image.open(BytesIO(resp.content)).resize((145, 145))
                avatar_im.paste(tmp_im, mask=tmp_im)
        elif avatar.startswith(('http://', 'https://')):
            async with httpx.AsyncClient() as client:
                avatar_im = Image.open(BytesIO(await client.get(avatar))).resize((145, 145))
    else:
        avatar_im = avatar_bg.copy()
        tmp_im = (await get_avatar(data_characters[0]["image"])).resize((145, 145))
        avatar_im.paste(tmp_im, mask=tmp_im)
    canvas.paste(avatar_im, (106, 86), mask=avatar_bg)

    f_draw.multiline_text((325, 435), fill='#404040', font=font_stats, spacing=23, anchor='mm',
                          text='{active_day_number}\n{achievement_number}\n'
                               '{avatar_number}\n{spiral_abyss}\n{domain_number}'.format(**data_stats))
    f_draw.multiline_text((665, 435), fill='#404040', font=font_stats, spacing=23, anchor='mm',
                          text='{common_chest_number}\n{exquisite_chest_number}\n{precious_chest_number}\n'
                               '{luxurious_chest_number}\n{magic_chest_number}'.format(**data_stats))
    f_draw.multiline_text((990, 435), fill='#404040', font=font_stats, spacing=23, anchor='mm',
                          text='{anemoculus_number}\n{geoculus_number}\n'
                               '{electroculus_number}\n\n'.format(**data_stats))
    # 角色背包
    for col in range(cols):
        col_start_y = head_bg.size[1] + col * middle_bg.size[1]
        canvas.paste(middle_bg, (0, col_start_y))
        rows = character_amount - (character_amount // 7) * 7 if col == cols - 1 and character_amount % 7 != 0 else 7
        for row in range(rows):
            character_index = col * 7 + row
            character = data_characters[character_index]
            character_avatar = (await get_avatar(character["image"])).resize((136, 136))
            character_avatar_x = 95 + (50 + character_avatar.size[0]) * row  # 头像边距145， 两头像间距50，故左边距95
            character_avatar_y = col_start_y + 40
            card_pos = (character_avatar_x - 12, character_avatar_y - 12)
            character_bg_canvas.paste(character_card_rgb[character['element']], card_pos)
            character_front.paste(character_card_bg, card_pos)
            character_front.paste(character_avatar, (character_avatar_x, character_avatar_y), mask=character_avatar)
            f_draw.text((character_avatar_x + 68, character_avatar_y + 152),
                        fill='black', text=character["name"], font=font_character_card, anchor='mm')
            f_draw.text((character_avatar_x + 48, character_avatar_y + 172),
                        fill='#4bbb75', text=f'Lv.{character["level"]}', font=font_character_card, anchor='mm')
            f_draw.text((character_avatar_x + 94, character_avatar_y + 172),
                        fill='#e71bb2', text=f'❤{character["fetter"]}', font=font_character_card, anchor='mm')

    character_bg_canvas = \
        ImageEnhance.Brightness(character_bg_canvas.filter(ImageFilter.GaussianBlur(config["enhance1"]))).enhance(3) \
        if config["Enhance"] else character_bg_canvas.filter(ImageFilter.GaussianBlur(config["enhance0"]))
    canvas.paste(character_bg_canvas, mask=character_bg_canvas.split()[3])
    canvas.paste(character_front, mask=character_front.split()[3])
    t1 = time()
    print('Total:', t1 - t2)
    return canvas


if __name__ == '__main__':
    import asyncio
    import json

    with open(r'F:\wansn_dir\project\IGS\user_info.json', 'r', encoding='utf-8') as u:
        data_ = json.load(u)
    im: Image.Image = asyncio.run(user_info(data_))
    im.show()
