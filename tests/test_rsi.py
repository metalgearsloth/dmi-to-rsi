from PIL import Image
from src.rsi import (
    RSIState,
    meta_json_to_states,
    RSI,
)
from tempfile import TemporaryDirectory
import os
from io import BytesIO
from tests.test_fixtures import (
    rsi_state,
    textures_repository,
    temporary_directory,
)

# TODO: ADD MORE TESTS, IGNORE ASYNC


def test_create_rsi_state():
    image = Image.new("P", (32, 32))
    state = RSIState(name="Dummy", data=image)


def test_create_rsi():
    rsi = RSI()


def test_open_rsi_as_states(textures_repository):
    meta_json_to_states(os.path.join(textures_repository, "light_small.rsi"))


def test_open_existing_rsi(textures_repository: str):
    path = os.path.join(textures_repository, "light_small.rsi")
    # TODO: Make it a fixture ya bum
    rsi = RSI(path)


def test_save_rsi(textures_repository: str, temporary_directory: TemporaryDirectory):
    path = os.path.join(textures_repository, "light_small.rsi")
    rsi = RSI(path)
    rsi.save_to(os.path.join(temporary_directory.name, "light_small.rsi"))


def test_save_rsi_state_image_to_buffer(rsi_state: RSIState):
    assert isinstance(rsi_state.image_buffer(), BytesIO) is True
