from PIL import ImageFont, Image
import aiofiles
import httpx

import os
from pathlib import Path

AVATAR_DIR = Path(__file__).parent.parent / "avatars"
if not AVATAR_DIR:
    AVATAR_DIR.mkdir()


async def get_avatar(url) -> Image.Image:
    filename = url.split('/')[-1:][0]
    file_path = AVATAR_DIR / filename
    if file_path.exists():
        return Image.open(file_path)
    async with httpx.AsyncClient() as c:
        resp = await c.get(url)
        if resp.status_code != 200:
            raise httpx.RequestError
    with open(file_path, 'wb+') as f:
        f.write(resp.content)
    return Image.open(file_path)


def get_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def get_font(size, w='85'):
    return ImageFont.truetype(get_path('assets', f'HYWenHei {w}W.ttf'),
                              size=size)


async def require_file(file=None,
                       r_mode='rb',
                       encoding=None,
                       url=None,
                       use_cache=True,
                       w_mode='wb',
                       timeout=30):
    async def read():
        async with aiofiles.open(file, r_mode, encoding=encoding) as fp:
            return await fp.read()

    if not any([file, url]):
        raise ValueError('file or url not null')

    file = file and Path(file)

    if file and file.exists() and use_cache:
        return await read()

    if not url:
        raise ValueError('url not null')

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=timeout)
        content = res.content
    except httpx.ConnectError:
        raise

    if file:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, w_mode) as f:
            f.write(content)
    return await read()


class stats:
    def __init__(self, data, max_hide=False):
        self.data = data
        self.max_hide = max_hide

    @property
    def active_day(self) -> int:
        return self.data['active_day_number']

    @property
    def active_day_str(self) -> str:
        return '????????????: %s' % self.active_day

    @property
    def achievement(self) -> int:
        return self.data['achievement_number']

    @property
    def achievement_str(self) -> str:
        return '???????????????: %s' % self.achievement

    @property
    def anemoculus(self) -> int:
        return self.data['anemoculus_number']

    @property
    def anemoculus_str(self) -> str:
        if self.max_hide and self.anemoculus == 66:
            return ''
        return '?????????: %s/66' % self.anemoculus

    @property
    def geoculus(self) -> int:
        return self.data['geoculus_number']

    @property
    def geoculus_str(self) -> str:
        if self.max_hide and self.geoculus == 131:
            return ''
        return '?????????: %s/131' % self.geoculus

    @property
    def electroculus(self) -> int:
        return self.data['electroculus_number']

    @property
    def electroculus_str(self) -> str:
        if self.max_hide and self.electroculus == 95:
            return ''
        return '?????????: %s/95' % self.electroculus

    @property
    def avatar(self) -> int:
        return self.data['avatar_number']

    @property
    def avatar_str(self) -> str:
        return '???????????????: %s' % self.avatar

    @property
    def way_point(self) -> int:
        return self.data['way_point_number']

    @property
    def way_point_str(self) -> str:
        # if self.max_hide and self.way_point == 83:
        #     return ''
        return '???????????????: %s' % self.way_point

    @property
    def domain(self) -> int:
        return self.data['domain_number']

    @property
    def domain_str(self) -> str:
        return '????????????: %s' % self.domain

    @property
    def spiral_abyss(self) -> str:
        return self.data['spiral_abyss']

    @property
    def spiral_abyss_str(self) -> str:
        return '' if self.spiral_abyss == '-' else '??????????????????: %s' % self.spiral_abyss

    @property
    def common_chest(self) -> int:
        return self.data['common_chest_number']

    @property
    def common_chest_str(self) -> str:
        return '????????????: %s' % self.common_chest

    @property
    def exquisite_chest(self) -> int:
        return self.data['exquisite_chest_number']

    @property
    def exquisite_chest_str(self) -> str:
        return '????????????: %s' % self.exquisite_chest

    @property
    def luxurious_chest(self) -> int:
        return self.data['luxurious_chest_number']

    @property
    def luxurious_chest_str(self) -> str:
        return '????????????: %s' % self.luxurious_chest

    @property
    def precious_chest(self) -> int:
        return self.data['precious_chest_number']

    @property
    def precious_chest_str(self) -> str:
        return '????????????: %s' % self.precious_chest

    @property
    def string(self):
        str_list = [
            self.active_day_str,
            self.achievement_str,
            self.anemoculus_str,
            self.geoculus_str,
            self.electroculus_str,
            self.avatar_str,
            self.way_point_str,
            self.domain_str,
            self.spiral_abyss_str,
            self.luxurious_chest_str,
            self.precious_chest_str,
            self.exquisite_chest_str,
            self.common_chest_str
        ]
        return '\n'.join(list(filter(None, str_list)))
