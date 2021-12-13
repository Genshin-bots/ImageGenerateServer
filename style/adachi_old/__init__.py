from PIL import Image, ImageFont, ImageFilter, ImageDraw, ImageEnhance
import httpx
import toml

from io import BytesIO
from pathlib import Path

config = toml.load(Path(__file__).parent / "config.toml")
ASSETS = Path(__file__).parent / "assets"
AVATARS = Path(__file__).parent.parent / "avatars"
head_bg: Image.Image = Image.open(ASSETS / "uid-upper-v2-2.png")
middle_bg: Image.Image = Image.open(ASSETS / "card-middle.png")
footer_bg: Image.Image = Image.open(ASSETS / "card-bottom.png")
character_card_bg: Image.Image = Image.open(ASSETS / "character_card_bg.png")
avatar_bg: Image.Image = Image.open(ASSETS / "avatar.png")
ar_wl_bg: Image.Image = Image.open(ASSETS / "ar_wl.png")
character_card_rgb = {}

font_small = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=13)
font_middle = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=22)
font_big = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=28)
font_large = ImageFont.truetype(str(ASSETS / "hywh_emoji-sym.ttf"), size=33)

for c in config["Colors"]:
    element_color = config["Colors"][c] if config["Colors"][c] != "" else None
    tmp_bg = Image.new('RGBA', (180, 240), None)
    tmp_bg.paste(Image.new('RGBA', (160, 220), color=element_color), (10, 10), mask=character_card_bg.split()[3])
    tmp_bg = ImageEnhance.Brightness(tmp_bg.filter(ImageFilter.GaussianBlur(2))).enhance(3)
    tmp_bg.paste(character_card_bg, (10, 10), mask=character_card_bg.split()[3])
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
    uid = f'UID: {kwargs.get("uid")}' if 'uid' in kwargs else ""
    nickname = kwargs.get('nickname', '')
    avatar = kwargs.get('avatar', None)
    ar = kwargs.get('ar', None)
    wl = kwargs.get('wl', None)

    data_characters = data["data"]["avatars"]
    data_stats = data["data"]["stats"]
    data_exp = {
        str(x["id"]): {
            "name": x["name"],
            "lvl": f'Lv. {x["level"]}',
            "percentage": f'{x["exploration_percentage"] / 10} %' if x["exploration_percentage"] != 1000 else '100 %',
            "offerings": x["offerings"]
        } for x in data["data"]["world_explorations"]
    }
    # 计算
    character_amount = len(data_characters)
    cols = character_amount // 7 if character_amount % 7 == 0 else character_amount // 7 + 1
    canvas_height = head_bg.size[1] + cols * middle_bg.size[1] + footer_bg.size[1]
    canvas = Image.new('RGBA', (middle_bg.size[0], canvas_height), None)

    c_draw = ImageDraw.Draw(canvas)
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

    if ar and wl:
        canvas.paste(ar_wl_bg, (714, 60))

    c_draw.text((328, 135), fill='#404040', text=nickname, font=font_large, anchor='lt')  # 昵称
    c_draw.text((330, 170), fill='#4bbb75', text=uid, font=font_middle, anchor='lt')  # UID

    c_draw.text((390, 644), text=data_exp['1']["percentage"], font=font_big, anchor='lt')
    c_draw.text((390, 695), text=data_exp['1']['lvl'], font=font_big, anchor='lt')
    c_draw.text((390, 817), text=data_exp['2']["percentage"], font=font_big, anchor='lt')
    c_draw.text((390, 869), text=data_exp['2']['lvl'], font=font_big, anchor='lt')
    c_draw.text((902, 644), text=data_exp['3']["percentage"], font=font_big, anchor='lt')
    c_draw.text((902, 695), text=data_exp['3']['lvl'], font=font_big, anchor='lt')
    c_draw.text((902, 807), text=data_exp['4']["percentage"], font=font_big, anchor='lt')
    c_draw.text((902, 844), text=data_exp['4']['lvl'], font=font_big, anchor='lt')
    c_draw.text((902, 881), text=f"Lv. {data_exp['4']['offerings'][0].get('level')}", font=font_big, anchor='lt')

    c_draw.multiline_text((325, 435), fill='#404040', font=font_large, spacing=23, anchor='mm',
                          text='{active_day_number}\n{achievement_number}\n'
                               '{avatar_number}\n{spiral_abyss}\n{domain_number}'.format(**data_stats))
    c_draw.multiline_text((665, 435), fill='#404040', font=font_large, spacing=23, anchor='mm',
                          text='{common_chest_number}\n{exquisite_chest_number}\n{precious_chest_number}\n'
                               '{luxurious_chest_number}\n{magic_chest_number}'.format(**data_stats))
    c_draw.multiline_text((990, 435), fill='#404040', font=font_large, spacing=23, anchor='mm',
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
            character_colored_bg = character_card_rgb.get(character['element'])
            canvas.paste(character_colored_bg, (card_pos[0] - 10, card_pos[1] - 10), character_colored_bg.split()[3])
            canvas.paste(character_avatar, (character_avatar_x, character_avatar_y), mask=character_avatar)
            c_draw.text((character_avatar_x + 68, character_avatar_y + 152),
                        fill='black', text=character["name"], font=font_small, anchor='mm')
            c_draw.text((character_avatar_x + 48, character_avatar_y + 172),
                        fill='#4bbb75', text=f'Lv.{character["level"]}', font=font_small, anchor='mm')
            c_draw.text((character_avatar_x + 94, character_avatar_y + 172),
                        fill='#e71bb2', text=f'❤{character["fetter"]}', font=font_small, anchor='mm')
    return canvas


if __name__ == '__main__':
    import asyncio
    import time
    import json

    with open(r'F:\wansn_dir\project\IGS\user_info.json', 'r', encoding='utf-8') as u:
        data_ = json.load(u)
    t1 = time.time()
    im: Image.Image = asyncio.run(user_info(data_))
    t2 = time.time()
    print('Total:', t2 - t1)
    im.show()
