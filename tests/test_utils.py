from src.utils import convert_dmi_to_rsi
from tempfile import TemporaryDirectory
import os
from tests.test_fixtures import (
    temporary_directory,
)


TEXTURES_DIRECTORY = os.path.join(os.path.dirname(__file__), "textures")


def test_convert_dmi_to_rsi(temporary_directory: TemporaryDirectory):
    source_dmi = os.path.join(TEXTURES_DIRECTORY, "stationobjs.dmi")
    target_rsi = os.path.join(temporary_directory.name, "convert_rsi_test.rsi")
    convert_dmi_to_rsi(source_dmi, target_rsi)
