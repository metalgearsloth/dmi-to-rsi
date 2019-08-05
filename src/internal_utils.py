import os
from io import BytesIO, StringIO

from PIL import Image

from logging import Logger, getLogger

logger: Logger = getLogger(__name__)


def png_dimensions(png_bytes) -> tuple:
    """
    Reads png bytes and gets (width, height)
    :param png_bytes: png bytes
    :return:
    """
    width = None
    height = None
    last_four_bytes = [0, 0, 0, 0]
    if isinstance(png_bytes, BytesIO):
        png_bytes.seek(0)
        png_bytes = png_bytes.read()
    for idx, b in enumerate(png_bytes):
        last_four_bytes.pop(0)
        last_four_bytes.append(b)
        if ["I", "H", "D", "R"] == [str(chr(x)) for x in last_four_bytes]:
            width = png_bytes[idx + 1: idx + 5]
            width = int.from_bytes(width, byteorder="big")
            height = png_bytes[idx + 5: idx + 9]
            height = int.from_bytes(height, byteorder="big")
    dimensions = (width, height)
    if width is None or height is None:
        raise Exception("Unable to get dimensions from png")
    return dimensions


def handle_data_to_pil_image(data) -> Image.Image:
    if isinstance(data, Image.Image):
        return data
    elif isinstance(data, BytesIO):
        data.seek(0)
        return Image.open(data)
    elif isinstance(data, bytes):
        # TODO: Need to test this
        size = png_dimensions(data)
        return Image.frombytes(mode="RGBA", size=size, data=data)
    elif os.path.exists(data):
        return Image.open(data)
    else:
        raise AttributeError("Unable to load data attribute")


def handle_new_pil_image(data) -> Image.Image:
    """
    Used for .rsi: Will create a new image if requiredwhereas _handle_pil_image will die (mainly used for .dmi files)
    :param data:
    :return:
    """
    try:
        return handle_data_to_pil_image(data)
    except AttributeError:
        return Image.new(mode="RGBA", size=(32, 32))
    except Exception as e:
        logger.critical(e)
        raise e


def stack_image(max_width: int= 3, dimensions: tuple=(32, 32)) -> Image.Image:
    """
    Most other functions dump images in a line for simplicity but this will re-stack it to 3 max columns or w/e
    :param max_width:
    :param dimensions:
    :return:
    """
    # TODO
    raise NotImplementedError