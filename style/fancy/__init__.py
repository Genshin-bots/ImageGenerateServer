from pathlib import Path
import os

import toml
import httpx
from PIL import Image
from PIL.ImageColor import getcolor
from PIL.ImageDraw import Draw
from PIL.ImageFilter import GaussianBlur
from PIL.ImageFont import FreeTypeFont

__all__ = [
    "user_info",
    "abyss"
]
__args__ = [
    ["-c", "--color"],
    ("bg", {"action": "store"})
]

FILE_PATH = Path(__file__).parent
conf = toml.load(FILE_PATH / 'config.toml')
AVATAR_PATH = FILE_PATH.parent / 'avatars'
ASSETS = FILE_PATH / 'assets'
IMAGES = ASSETS / 'images'
font_card = FreeTypeFont(str(ASSETS / 'din-bold-2.ttf'), 14)
font_head = FreeTypeFont(str(ASSETS / 'zh-cn.ttf'), 22)
font_st = FreeTypeFont(str(ASSETS / 'din-bold-2.ttf'), 26)
head_raw_left = '活跃天数：{active_day_number}\n拥有角色：{avatar_number}\n获得成就：{achievement_number}\n解锁锚点：{' \
                'way_point_number}\n解锁秘境：{domain_number}'
head_raw_right = '普通宝箱：{common_chest_number}\n精致宝箱：{exquisite_chest_number}\n珍贵宝箱：{precious_chest_number}\n华丽宝箱：{' \
                 'luxurious_chest_number}\n奇馈宝箱：{magic_chest_number}'

if not IMAGES.exists():
    IMAGES.mkdir()


def mk_suit(im1, im2):
    """"
    使im1与im2等宽
    """
    return im1.resize((im2.size[0], round(im2.size[0] / im1.size[0] * im1.size[1])))


async def get_image(url: str, folder=IMAGES) -> Image.Image:
    offline_image = Path(folder) / url.split('/')[-1:][0]
    if offline_image.exists():
        return Image.open(offline_image)
    async with httpx.AsyncClient() as c:
        resp = await c.get(url)
        if resp.status_code != 200:
            raise httpx.ConnectError
    with open(offline_image, 'wb') as tmp_icon:
        tmp_icon.write(resp.content)
    return Image.open(offline_image)


font_color = getcolor(conf["main"]["text_color"], 'RGB')

# 静态图像
head_mask: Image.Image = Image.open(ASSETS / 'user_info_ver2_mask.png')
head_area: Image.Image = Image.open(ASSETS / 'user_info_ver2_mask_area.png').split()[3]
head_icons: Image.Image = Image.open(ASSETS / 'user_info_ver2_icons.png')
card: Image.Image = Image.open(ASSETS / 'card.png')
card = card.resize((122, 150))
text_bg = Image.new('RGB', head_area.size, color=font_color)
cf = Image.open(ASSETS / 'cf.png').resize((49, 14))  # constellations and friendship icon


async def user_info(data_: dict, **kwargs):
    bg_url = kwargs.get('bg_url') if 'bg_url' in kwargs else None
    # 背景图像
    background_img: Image.Image = await get_image(bg_url) if bg_url else Image.open(ASSETS / 'xh.jpg')
    background_img = mk_suit(background_img, head_mask)
    # 动态图像数量计算
    character_amount = len(data_["data"]["avatars"])
    row_amount = character_amount // 7  # 行数
    end_line_cols = character_amount % 7
    row_amount = row_amount + 1
    total_height = (50 * 2 + head_mask.size[1] + 30 * (row_amount - 1) + (row_amount - 2) * 160
                    if end_line_cols == 0
                    else 50 * 2 + head_mask.size[1] + 30 * row_amount + (row_amount - 1) * 160) + 100
    # 新建图层
    static_image = Image.new('RGBA', (1080, total_height))
    background_mask = Image.new('RGBA', (1080, total_height))
    background_mask.paste(head_mask, (0, 0))
    d_si = Draw(static_image)
    # 头部
    static_image.paste(head_icons, (0, 0))  # 拼贴静态图标
    static_image.paste(text_bg, (580, 90), mask=head_area)
    stats = data_["data"]["stats"]
    d_si.multiline_text((90, 100), head_raw_left.format(**stats), spacing=10,
                        fill=font_color, font=font_head, anchor='la')  # 左侧信息文本锚点(LeftMiddle:lm)
    d_si.multiline_text((310, 100), head_raw_right.format(**stats), spacing=10,
                        fill=font_color, font=font_head, anchor='la')  # 左侧信息文本锚点(LeftMiddle:lm)
    d_si.text((160, 300), str(stats["anemoculus_number"]), fill=font_color, font=font_st, anchor='mm')
    d_si.text((285, 300), str(stats["geoculus_number"]), fill=font_color, font=font_st, anchor='mm')
    d_si.text((425, 300), str(stats["electroculus_number"]), fill=font_color, font=font_st, anchor='mm')
    d_si.text((640, 455), stats["spiral_abyss"], fill=(220, 220, 220), font=font_st, anchor='mm')
    # 角色卡片
    for row in range(row_amount):
        col_amount = end_line_cols if end_line_cols < 7 and row == row_amount - 1 else 7
        for c in range(col_amount):
            character_index = (row - 1) * 7 + c if end_line_cols == 0 and row == row_amount else row * 7 + c
            card_pos_x = 50 + c * (122 + 21)
            card_pos_y = head_mask.size[1] + (row - 1) * (150 + 30) \
                if end_line_cols == 0 and row == row_amount else head_mask.size[1] + row * (150 + 30)
            c_icon_pos = (card_pos_x + 16, card_pos_y + 16)
            character = data_["data"]["avatars"][character_index]
            character_icon = (await get_image(character["image"], AVATAR_PATH)).resize((90, 90))
            static_image.paste(character_icon, c_icon_pos)
            static_image.paste(cf, (c_icon_pos[0] + 10, c_icon_pos[1] + 110))
            d_si.text((c_icon_pos[0] + 45, c_icon_pos[1] + 100),
                      f'Lv. {character["level"]}', fill=font_color, font=font_card, anchor='mm')  # 等级
            d_si.text((c_icon_pos[0] + 28, c_icon_pos[1] + 112), str(character["fetter"]),
                      fill=font_color, font=font_card, anchor='lt')  # 好感度(文本锚点MiddleMiddle:mm)
            d_si.text((c_icon_pos[0] + 64, c_icon_pos[1] + 112), str(character["actived_constellation_num"]),
                      fill=font_color, font=font_card, anchor='lt')  # 命座
            background_mask.paste(card, (card_pos_x, card_pos_y), mask=card.split()[3])
    # 贴合图层
    background_img = background_img.crop((0, 0, *background_mask.size))
    panel_ = background_img.copy()
    colored_panel = Image.new('RGBA', background_img.size, (*getcolor(conf["main"]["panel_color"], 'RGB')[:3],
                                                            int(conf["main"]["panel_trans"] / 100 * 255)))
    panel_.paste(colored_panel, mask=colored_panel)
    panel = panel_.filter(GaussianBlur(radius=20))
    background_img.paste(panel, mask=background_mask.split()[3])
    background_img.paste(static_image, mask=static_image.split()[3])
    return background_img


async def abyss():
    pass


if __name__ == '__main__':
    from time import time
    import json

    with open(FILE_PATH.parent.parent / 'user_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    t2 = time()
    b = user_info(data)
    t1 = time()
    print(t1 - t2)
    b.show()
