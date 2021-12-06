from .utils import get_font, get_path, require_file, stats, get_avatar
from .imghandler import *

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

assets_dir = Path(__file__).parent / 'assets'
CHARA_CARD = assets_dir / 'chara_card'
info_bg = Image.open(assets_dir / "原神资料卡.png")
weapon_bg = Image.open(assets_dir / "weapon_bg.png")
weapon_icon_dir = assets_dir / 'weapon'
abyss_star_bg = Image.open(assets_dir / "深渊星数.png").convert('RGBA')
avatar_bgs = {i: Image.open(assets_dir / f"UI_QualityBg_{i}.png") for i in [4, 5, 105]}
chara_footer = Image.open(assets_dir / "chara_footer.png")
chara_crop_mask = Image.open(assets_dir / "chara_crop_mask.png")

weapon_card_bg = {}
for i in range(1, 6):
    weapon_card_bg[i] = Image.open(assets_dir / f"{i}星武器.png")

if not CHARA_CARD.exists():
    CHARA_CARD.mkdir()

Use_Avatar = True  # 是否使用头像

# 以下2个选项控制显示深渊星数 已经角色武器信息, 可能会使用额外的cookie次数
# 已知每个cookie能查询30次, 查询基本信息为一次, 深渊信息为一次, 武器信息为一次
# 下列2个变量都为True时 查询次数为3次
SHOW_SPIRAL_ABYSS_STAR = True  # 是否显示深渊信息
SHOW_WEAPON_INFO = True  # 是否显示武器信息

AVATARS = assets_dir.parent / "avatars"


async def gen_char_card(character_data, return_pil_obj=False) -> Image.Image:
    filename = character_data["image"].split('/')[-1:][0]
    file_path = CHARA_CARD / filename
    if file_path.exists():
        return Image.open(file_path)
    chara_card_canvas = Image.new('RGBA', (250, 304), None)
    avatar_ = (await get_avatar(character_data["image"])).resize((220, 220))
    element_icon = Image.open(Path(assets_dir / f'{character_data["element"]}.png'))
    avatar_bg: Image.Image = avatar_bgs[character_data["rarity"]]
    avatar_bg = avatar_bg.resize((250, 304))
    avatar_bg.paste(avatar_, (15, 20), mask=avatar_.split()[3])
    avatar_bg.paste(chara_footer, (10, 200), mask=chara_footer.split()[3])
    chara_card_canvas.paste(avatar_bg, (0, 0), mask=chara_crop_mask)
    chara_card_canvas = chara_card_canvas.crop((12, 11, 238, 293))
    chara_card_canvas.paste(element_icon, (5, 5), mask=element_icon.split()[3])
    chara_card_canvas.save(file_path)
    if return_pil_obj:
        return chara_card_canvas


async def avatar_card(character_data):
    """
    生成角色缩略信息卡
    avatar_id：角色id
    level：经验等级
    constellation：命之座等级
    fetter：好感度等级
    """
    card = Image.open(
        CHARA_CARD / character_data["image"].split("/")[-1:][0])  # await get_avatar(character_data["image"])
    draw_text_by_line(card, (0, 235), f'Lv.{character_data["level"]}', get_font(35), '#475463', 226, True)
    if character_data["actived_constellation_num"] > 0:
        i_con = Image.open(os.path.join(assets_dir, f'命之座{character_data["actived_constellation_num"]}.png'))
        card = easy_alpha_composite(card, i_con, (160, -5))

    i_fet = Image.open(os.path.join(assets_dir, f'好感度{character_data["fetter"]}.png'))
    card = easy_alpha_composite(card, i_fet, (0, 165))

    # 显示详细信息
    if "weapon" in character_data:
        # 武器信息
        detail_info = character_data
        weapon_info = detail_info["weapon"]
        new_card = Image.new("RGBA", (card.width, card.height + weapon_bg.height))
        new_card = easy_alpha_composite(new_card, card, (0, 0))

        # 武器背景
        weapon_card = weapon_bg.copy()
        new_weapon_card_bg = weapon_card_bg[weapon_info["rarity"]].copy()
        # 武器等级

        weapon_card = easy_alpha_composite(weapon_card, new_weapon_card_bg, (4, 3))
        # 获取武器图标
        file_url = weapon_info.icon
        file_name = Path(file_url).name
        weapon_icon_img = await require_file(file=weapon_icon_dir / file_name, url=file_url)
        weapon_icon = Image.open(BytesIO(weapon_icon_img)).convert("RGBA").resize((56, 65), Image.LANCZOS)
        weapon_card = easy_alpha_composite(weapon_card, weapon_icon, (9, 6))

        # 武器名称 精炼
        name_img = Image.new("RGBA", (weapon_bg.width - new_weapon_card_bg.width, weapon_bg.height))
        draw_text_by_line(name_img, (96.86, 9.71), weapon_info.name, get_font(18), '#475463', 226, True)

        draw_text_by_line(name_img, (132.48, 34.01), f'Lv.{weapon_info.level}', get_font(14), '#475463', 226, True)

        affix_name = weapon_info.affix_level == 5 and 'MAX' or f'{weapon_info.affix_level}阶'
        draw_text_by_line(name_img, (120, 53.39), f'精炼{affix_name}', get_font(18), '#cc9966', 226, True)

        weapon_card = easy_alpha_composite(weapon_card, name_img, (new_weapon_card_bg.width, 0))

        # 复制到新的卡片上
        new_card = easy_alpha_composite(new_card, weapon_card, (0, card.height))

        card = new_card

    return card


async def user_info(raw_data, **kwargs):
    """
    绘制玩家资料卡
    """
    uid = kwargs.get('uid') if 'uid' in kwargs else ""
    avatar = kwargs.get('qid') if 'qid' in kwargs else ""
    nickname = kwargs.get('nickname') if 'nickname' in kwargs else ""
    max_chara = kwargs.get('max_chara') if 'max_chara' in kwargs else None
    abyss_star = kwargs.get('abyss_star') if 'abyss_star' in kwargs else None

    stats_ = stats(raw_data["data"]["stats"], True)
    world_explorations = {}
    for w in raw_data["data"]["world_explorations"]:
        if isinstance(w['exploration_percentage'], int):
            w["exploration_percentage"] = str(w['exploration_percentage'] / 10)
            if w["exploration_percentage"] == '100.0':
                w["exploration_percentage"] = '100'
        world_explorations[w["name"]] = w

    char_data = raw_data["data"]["avatars"]
    for c in char_data:
        await gen_char_card(c)

    for k in char_data:
        if k['name'] == '旅行者':
            k['rarity'] = 3
        if k['name'] == '埃洛伊':
            k['rarity'] = 3

    char_data = sorted(char_data, key=lambda x: (-x['rarity'], -x['actived_constellation_num'], -x['level']))

    # 头像
    if Use_Avatar and avatar:
        avatar_url = f'https://q.qlogo.cn/headimg_dl?dst_uin={avatar}&spec=640&img_type=jpg' if avatar.isdigit() else None
        avatar_url = avatar if not avatar_url and avatar.startswith(('http://', 'https://')) else None
        avatar_pic = await get_pic(avatar_url, (256, 256)) if avatar_url else Image.new('RGBA', (256, 256), None)
    else:
        avatar_pic = await get_avatar(char_data[0]["image"])
    card_bg = Image.new('RGB', (1080, 1820), '#d19d78')
    easy_paste(card_bg, avatar_pic, (412, 140))
    easy_paste(card_bg, info_bg, (0, 0))
    text_draw = ImageDraw.Draw(card_bg)
    # UID
    text_draw.text((812, 10), f'UID：{uid}', '#ffffff', get_font(30))
    # 用户昵称
    draw_text_by_line(card_bg, (0, 528), nickname[:10], get_font(40), '#786a5d', 450, True)
    # 成就数量
    text_draw.text((238, 768), stats_.achievement.__str__(), '#475463', get_font(60))
    # 深境螺旋
    text_draw.text((769, 768), stats_.spiral_abyss, '#475463', get_font(60))
    # 活跃天数
    text_draw.text((350, 1032), stats_.active_day.__str__(), '#caae93', get_font(36))
    # 获得角色
    text_draw.text((350, 1086), stats_.avatar.__str__(), '#caae93', get_font(36))
    # 开启锚点
    text_draw.text((350, 1142), stats_.way_point.__str__(), '#caae93', get_font(36))
    # 探索秘境
    text_draw.text((350, 1197), stats_.domain.__str__(), '#caae93', get_font(36))
    # 普通宝箱
    text_draw.text((860, 1032), stats_.common_chest.__str__(), '#caae93', get_font(36))
    # 精致宝箱
    text_draw.text((860, 1086), stats_.exquisite_chest.__str__(), '#caae93', get_font(36))
    # 珍贵宝箱
    text_draw.text((860, 1142), stats_.precious_chest.__str__(), '#caae93', get_font(36))
    # 华丽宝箱
    text_draw.text((860, 1197), stats_.luxurious_chest.__str__(), '#caae93', get_font(36))
    # 蒙德
    world = world_explorations['蒙德']
    text_draw.text((370, 1370), str(world["exploration_percentage"]) + '%', '#d4aa6b', get_font(32))
    text_draw.text((370, 1414), 'Lv.' + str(world["level"]), '#d4aa6b', get_font(32))
    text_draw.text((370, 1456), stats_.anemoculus.__str__(), '#d4aa6b', get_font(32))
    # 璃月
    world = world_explorations['璃月']
    text_draw.text((896, 1370), str(world["exploration_percentage"]) + '%', '#d4aa6b', get_font(32))
    text_draw.text((896, 1414), 'Lv.' + str(world["level"]), '#d4aa6b', get_font(32))
    text_draw.text((896, 1456), stats_.geoculus.__str__(), '#d4aa6b', get_font(32))
    # 雪山
    world = world_explorations['龙脊雪山']
    text_draw.text((350, 1555), str(world["exploration_percentage"]) + '%', '#d4aa6b', get_font(32))
    text_draw.text((350, 1612), 'Lv.' + str(world["level"]), '#d4aa6b', get_font(32))
    # 稻妻
    world = world_explorations['稻妻']
    text_draw.text((880, 1543), str(world["exploration_percentage"]) + '%', '#d4aa6b', get_font(24))
    text_draw.text((880, 1576), 'Lv.' + str(world["level"]), '#d4aa6b', get_font(24))
    text_draw.text((880, 1606), 'Lv.' + str(world["offerings"][0]["level"]), '#d4aa6b', get_font(24))
    text_draw.text((880, 1639), stats_.electroculus.__str__(), '#d4aa6b', get_font(24))

    # 深渊星数
    if SHOW_SPIRAL_ABYSS_STAR and abyss_star:
        new_abyss_star_bg = abyss_star_bg.copy()
        draw_text_by_line(new_abyss_star_bg, (0, 60), str(abyss_star), get_font(36), '#78818b', 64,
                          True)
        card_bg = easy_alpha_composite(card_bg.convert('RGBA'), new_abyss_star_bg, (925, 710))

    detail_info_height = 0

    avatar_cards = []
    for chara in char_data[:max_chara or len(char_data)]:
        card = await avatar_card(chara)
        avatar_cards.append(card)

    chara_bg = Image.new('RGB', (1080, math.ceil(len(avatar_cards) / 4) *
                                 (315 + detail_info_height)), '#f0ece3')
    chara_img = image_array(chara_bg, avatar_cards, 4, 35, 0)

    info_card = Image.new('RGBA', (1080, card_bg.size[1] + chara_img.size[1]))
    easy_paste(info_card, card_bg.convert('RGBA'), (0, 0))
    easy_paste(info_card, chara_img.convert('RGBA'), (0, card_bg.size[1]))

    return info_card


if __name__ == '__main__':
    import json
    import asyncio

    with open(r'F:\wansn_dir\project\IGS\user_info.json', 'r', encoding='utf-8') as f:
        user_info_data = json.load(f)
    # im: Image.Image = asyncio.run(user_info(user_info_data))
    im: Image.Image = asyncio.run(gen_char_card(user_info_data["data"]["avatars"][0], True))
    im.show()
