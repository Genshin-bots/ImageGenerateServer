from PIL import Image
from .tweaks import *

import os
import sys
from pkgutil import iter_modules
from pathlib import Path

local_dir = Path(__file__).parent
sys.path.append(str(local_dir))

DEFAULT_STYLE = "fancy"
AVATARS = local_dir / 'avatars'

if not AVATARS.exists():
    AVATARS.mkdir()


class Style:
    def __init__(self):
        self.list = list(filter(lambda x: x.ispkg, iter_modules([str(local_dir)])))
        self.styles = {}
        for sn in self.list:
            self.styles[sn.name] = __import__(sn.name)

    async def user_info(self, name, raw_data, **kwargs) -> Image.Image:
        return await self.styles[name].user_info(raw_data, **kwargs)
