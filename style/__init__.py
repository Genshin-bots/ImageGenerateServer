from PIL import Image

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

    def user_info(self, name, raw_data, **kwargs) -> Image.Image:
        return self.styles[name].user_info(raw_data, **kwargs)


if __name__ == '__main__':
    from tweaks import timer
    import json

    with open('F:\\wansn_dir\\project\\user_info\\data_userinfo.json', 'r', encoding='utf-8') as f:
        u = json.load(f)
