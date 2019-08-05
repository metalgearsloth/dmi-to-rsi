import os
from tempfile import TemporaryDirectory

import pytest

from src.dmi import DMI
from src.rsi import meta_json_to_states


TEXTURES_REPOSITORY = os.path.join(os.path.dirname(__file__), "textures")


@pytest.fixture
def temporary_directory():
    tempfile = TemporaryDirectory()
    yield tempfile
    tempfile.cleanup()


@pytest.fixture
def textures_repository():
    return TEXTURES_REPOSITORY


@pytest.fixture
def existing_dmi():
    dmi_path = os.path.join(TEXTURES_REPOSITORY, "stationobjs.dmi")
    dmi = DMI(dmi_path)
    return dmi


@pytest.fixture
def rsi_state():
    path = os.path.join(TEXTURES_REPOSITORY, "light_small.rsi")
    states = meta_json_to_states(path)
    return states[0]