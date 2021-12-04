import os

import requests
import toml
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

FILE_PATH = os.path.split(__file__)[0]
conf = toml.load(os.path.join(FILE_PATH, 'config.toml'))
ICON_PATH = os.path.join(FILE_PATH, 'assets/icon')
font_card = FreeTypeFont(os.path.join(FILE_PATH, 'assets/din-bold-2.ttf'), 14)
font_head = FreeTypeFont(os.path.join(FILE_PATH, 'assets/zh-cn.ttf'), 22)
font_st = FreeTypeFont(os.path.join(FILE_PATH, 'assets/din-bold-2.ttf'), 26)
head_raw_left = '活跃天数：{active_day_number}\n拥有角色：{avatar_number}\n获得成就：{achievement_number}\n解锁锚点：{' \
                'way_point_number}\n解锁秘境：{domain_number}'
head_raw_right = '普通宝箱：{common_chest_number}\n精致宝箱：{exquisite_chest_number}\n珍贵宝箱：{precious_chest_number}\n华丽宝箱：{' \
                 'luxurious_chest_number}\n奇馈宝箱：{magic_chest_number}'

if not os.path.exists(ICON_PATH):
    os.makedirs(ICON_PATH)


def mk_suit(im1, im2):
    """"
    使im1与im2等宽
    """
    return im1.resize((im2.size[0], round(im2.size[0] / im1.size[0] * im1.size[1])))


def get_icon(url: str) -> Image.Image:
    offline_icon = os.path.join(ICON_PATH, url.split('/')[-1:][0])
    if os.path.exists(offline_icon):
        return Image.open(offline_icon)
    resp = requests.get(url).content
    with open(offline_icon, 'wb') as tmp_icon:
        tmp_icon.write(resp)
    return Image.open(offline_icon)


font_color = getcolor(conf["main"]["text_color"], 'RGB')

# 静态图像
head_mask: Image.Image = Image.open(os.path.join(FILE_PATH, 'assets/user_info_ver2_mask.png'))
head_area: Image.Image = Image.open(os.path.join(FILE_PATH, 'assets/user_info_ver2_mask_area.png')).split()[3]
head_icons: Image.Image = Image.open(os.path.join(FILE_PATH, 'assets/user_info_ver2_icons.png'))
card: Image.Image = Image.open(os.path.join(FILE_PATH, 'assets/card.png'))
card = card.resize((122, 150))
text_bg = Image.new('RGB', head_area.size, color=font_color)
cf = Image.open(os.path.join(FILE_PATH, 'assets/cf.png')).resize((49, 14))  # constellations and friendship icon


def user_info(data_: dict, **kwargs):
    bg_url = kwargs.get('bg_url') if 'bg_url' in kwargs else None
    # 背景图像
    background_img: Image.Image = get_icon(bg_url) if bg_url else Image.open(os.path.join(FILE_PATH, 'assets/xh.jpg'))
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
            character_icon = get_icon(character["image"]).resize((90, 90))
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


def abyss():
    pass


if __name__ == '__main__':
    from time import time

    data = {
        "retcode": 0,
        "message": "OK",
        "data": {
            "role": None,
            "avatars": [
                {
                    "id": 10000037,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Ganyu.png",
                    "name": "甘雨",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 90,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000042,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Keqing.png",
                    "name": "刻晴",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 90,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000046,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Hutao.png",
                    "name": "胡桃",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 90,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000051,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Eula.png",
                    "name": "优菈",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 90,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000002,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Ayaka.png",
                    "name": "神里绫华",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000022,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Venti.png",
                    "name": "温迪",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000041,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Mona.png",
                    "name": "莫娜",
                    "element": "Hydro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000052,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Shougun.png",
                    "name": "雷电将军",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000023,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Xiangling.png",
                    "name": "香菱",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000031,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Fischl.png",
                    "name": "菲谢尔",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000032,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Bennett.png",
                    "name": "班尼特",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000056,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Sara.png",
                    "name": "九条裟罗",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 89,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000038,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Albedo.png",
                    "name": "阿贝多",
                    "element": "Geo",
                    "fetter": 10,
                    "level": 88,
                    "rarity": 5,
                    "actived_constellation_num": 0
                },
                {
                    "id": 10000034,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Noel.png",
                    "name": "诺艾尔",
                    "element": "Geo",
                    "fetter": 10,
                    "level": 88,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000036,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Chongyun.png",
                    "name": "重云",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 88,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000003,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Qin.png",
                    "name": "琴",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 87,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000049,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Yoimiya.png",
                    "name": "宵宫",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 87,
                    "rarity": 5,
                    "actived_constellation_num": 0
                },
                {
                    "id": 10000029,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Klee.png",
                    "name": "可莉",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 86,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000033,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Tartaglia.png",
                    "name": "达达利亚",
                    "element": "Hydro",
                    "fetter": 10,
                    "level": 86,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000047,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kazuha.png",
                    "name": "枫原万叶",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 86,
                    "rarity": 5,
                    "actived_constellation_num": 2
                },
                {
                    "id": 10000025,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Xingqiu.png",
                    "name": "行秋",
                    "element": "Hydro",
                    "fetter": 10,
                    "level": 85,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000053,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Sayu.png",
                    "name": "早柚",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 85,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000035,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Qiqi.png",
                    "name": "七七",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 81,
                    "rarity": 5,
                    "actived_constellation_num": 3
                },
                {
                    "id": 10000016,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Diluc.png",
                    "name": "迪卢克",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 80,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000030,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Zhongli.png",
                    "name": "钟离",
                    "element": "Geo",
                    "fetter": 10,
                    "level": 80,
                    "rarity": 5,
                    "actived_constellation_num": 2
                },
                {
                    "id": 10000054,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kokomi.png",
                    "name": "珊瑚宫心海",
                    "element": "Hydro",
                    "fetter": 10,
                    "level": 80,
                    "rarity": 5,
                    "actived_constellation_num": 1
                },
                {
                    "id": 10000043,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Sucrose.png",
                    "name": "砂糖",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 80,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000045,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Rosaria.png",
                    "name": "罗莎莉亚",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 80,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000007,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_PlayerGirl.png",
                    "name": "旅行者",
                    "element": "Electro",
                    "fetter": 0,
                    "level": 80,
                    "rarity": 5,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000039,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Diona.png",
                    "name": "迪奥娜",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 79,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000026,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Xiao.png",
                    "name": "魈",
                    "element": "Anemo",
                    "fetter": 10,
                    "level": 70,
                    "rarity": 5,
                    "actived_constellation_num": 1
                },
                {
                    "id": 10000014,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Barbara.png",
                    "name": "芭芭拉",
                    "element": "Hydro",
                    "fetter": 10,
                    "level": 70,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000021,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Ambor.png",
                    "name": "安柏",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 70,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000024,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Beidou.png",
                    "name": "北斗",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 70,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000050,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Tohma.png",
                    "name": "托马",
                    "element": "Pyro",
                    "fetter": 3,
                    "level": 69,
                    "rarity": 4,
                    "actived_constellation_num": 0
                },
                {
                    "id": 10000015,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kaeya.png",
                    "name": "凯亚",
                    "element": "Cryo",
                    "fetter": 10,
                    "level": 61,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000006,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Lisa.png",
                    "name": "丽莎",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 60,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000020,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Razor.png",
                    "name": "雷泽",
                    "element": "Electro",
                    "fetter": 10,
                    "level": 50,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000048,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Feiyan.png",
                    "name": "烟绯",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 50,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000062,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Aloy.png",
                    "name": "埃洛伊",
                    "element": "Cryo",
                    "fetter": 9,
                    "level": 50,
                    "rarity": 105,
                    "actived_constellation_num": 0
                },
                {
                    "id": 10000027,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Ningguang.png",
                    "name": "凝光",
                    "element": "Geo",
                    "fetter": 10,
                    "level": 22,
                    "rarity": 4,
                    "actived_constellation_num": 6
                },
                {
                    "id": 10000044,
                    "image": "https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Xinyan.png",
                    "name": "辛焱",
                    "element": "Pyro",
                    "fetter": 10,
                    "level": 21,
                    "rarity": 4,
                    "actived_constellation_num": 6
                }
            ],
            "stats": {
                "active_day_number": 404,
                "achievement_number": 492,
                "win_rate": 0,
                "anemoculus_number": 66,
                "geoculus_number": 131,
                "avatar_number": 42,
                "way_point_number": 136,
                "domain_number": 31,
                "spiral_abyss": "12-3",
                "precious_chest_number": 291,
                "luxurious_chest_number": 114,
                "exquisite_chest_number": 1080,
                "common_chest_number": 1370,
                "electroculus_number": 181,
                "magic_chest_number": 45
            },
            "city_explorations": [],
            "world_explorations": [
                {
                    "level": 10,
                    "exploration_percentage": 1000,
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/city_icon/UI_ChapterIcon_Daoqi.png",
                    "name": "稻妻",
                    "type": "Reputation",
                    "offerings": [
                        {
                            "name": "神樱眷顾",
                            "level": 40
                        }
                    ],
                    "id": 4
                },
                {
                    "level": 12,
                    "exploration_percentage": 1000,
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/city_icon/UI_ChapterIcon_Dragonspine.png",
                    "name": "龙脊雪山",
                    "type": "Offering",
                    "offerings": [
                        {
                            "name": "忍冬之树",
                            "level": 12
                        }
                    ],
                    "id": 3
                },
                {
                    "level": 8,
                    "exploration_percentage": 1000,
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/city_icon/UI_ChapterIcon_Liyue.png",
                    "name": "璃月",
                    "type": "Reputation",
                    "offerings": [],
                    "id": 2
                },
                {
                    "level": 8,
                    "exploration_percentage": 1000,
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/city_icon/UI_ChapterIcon_Mengde.png",
                    "name": "蒙德",
                    "type": "Reputation",
                    "offerings": [],
                    "id": 1
                }
            ],
            "homes": [
                {
                    "level": 10,
                    "visit_num": 64,
                    "comfort_num": 21720,
                    "item_num": 1325,
                    "name": "罗浮洞",
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_HomeworldModule_2_Pic.png",
                    "comfort_level_name": "贝阙珠宫",
                    "comfort_level_icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_Homeworld_Comfort_10.png"
                },
                {
                    "level": 10,
                    "visit_num": 64,
                    "comfort_num": 21720,
                    "item_num": 1325,
                    "name": "翠黛峰",
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_HomeworldModule_1_Pic.png",
                    "comfort_level_name": "贝阙珠宫",
                    "comfort_level_icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_Homeworld_Comfort_10.png"
                },
                {
                    "level": 10,
                    "visit_num": 64,
                    "comfort_num": 21720,
                    "item_num": 1325,
                    "name": "清琼岛",
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_HomeworldModule_3_Pic.png",
                    "comfort_level_name": "贝阙珠宫",
                    "comfort_level_icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_Homeworld_Comfort_10.png"
                },
                {
                    "level": 10,
                    "visit_num": 64,
                    "comfort_num": 21720,
                    "item_num": 1325,
                    "name": "绘绮庭",
                    "icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_HomeworldModule_4_Pic.png",
                    "comfort_level_name": "贝阙珠宫",
                    "comfort_level_icon": "https://upload-os-bbs.mihoyo.com/game_record/genshin/home/UI_Homeworld_Comfort_10.png"
                }
            ]
        }
    }
    t2 = time()
    b = user_info(data)
    t1 = time()
    print(t1 - t2)
    b.show()
