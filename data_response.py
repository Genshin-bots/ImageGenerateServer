def success(msg, resp_type="Image"):
    return {
        "retcode": 0,
        "url" if resp_type == "Image" else resp_type.lower(): str(msg)
    }


def data_error(msg="Data Error"):
    return {
        "retcode": 1,
        "url": str(msg)
    }


def generator_error(msg="Generator Error"):
    return {
        "retcode": 2,
        "url": str(msg)
    }


def style_err(style_):
    return {
        "retcode": 3,
        "ErrorMsg": f"Style {style_} not found."
    }


def not_found(pth_=""):
    return {
        "retcode": 4,
        "ErrorMsg": "Path " + str(pth_) + " not found."
    }
