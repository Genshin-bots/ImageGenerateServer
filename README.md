![[object Object]](https://socialify.git.ci/Genshin-bots/ImageGenerateServer/image?description=1&font=KoHo&logo=https%3A%2F%2Fyuanshen.minigg.cn%2Fstatic%2Flogo.png&owner=1&pattern=Circuit%20Board&theme=Light)

<div align="center"><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/w/Genshin-bots/ImageGenerateServer?style=for-the-badge"> <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/Genshin-bots/ImageGenerateServer?color=orange&style=for-the-badge"> <img alt="Demo" src="https://img.shields.io/static/v1?label=Demo&message=MiniGG&color=critical&style=for-the-badge"></div>

> 不知道写啥.jpg
>
> 暂时只支持角色信息 深渊咕咕咕...



**Style List**：

- [ ] 🔜Text
- [x] ✅Fancy
- [ ] ♾️Color
- [ ] 💠[Adachi](https://github.com/Arondight/Adachi-BOT)
- [x] ✅[eGenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin)
- [ ] 🔜[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)

### POST 数据格式

```json
{
    "data": {
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
            }
	]
    }
}
```
实际data格式依选择的样式有所删减
