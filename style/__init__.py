from PIL import Image
from .tweaks import *

import os
import sys
import pkgutil

sys.path.append(os.path.split(__file__)[0])
DEFAULT_STYLE = "fancy"


class Style:
    def __init__(self):
        self.list = list(filter(lambda x: x.ispkg, pkgutil.iter_modules([os.path.split(__file__)[0]])))
        self.styles = {}
        for sn in self.list:
            self.styles[sn.name] = __import__(sn.name)

    async def user_info(self, name, raw_data, **kwargs) -> Image.Image:
        return await self.styles[name].user_info(raw_data, **kwargs)
