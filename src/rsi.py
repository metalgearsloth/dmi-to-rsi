import json
from logging import getLogger, Logger
from typing import List
import os
from PIL import Image
from io import BytesIO
from src.internal_utils import handle_data_to_pil_image

logger: Logger = getLogger(__name__)


class InvalidRSIStateException(Exception):
    pass


class RSIState:
    # Directions might be able to be more?
    def __init__(self,
                 data,
                 name: str = None,
                 directions: int = 1,
                 delays: list = None,
                 select: list = None,
                 flags: dict = None,
                 **kwargs,
                 ):
        self.image = handle_data_to_pil_image(data)  # RSIState should only ever get the completed image I think?
        self.name = name
        self.directions = directions  # TODO: Look at https://github.com/space-wizards/RSI
        # Don't use mutable in __init__ or Guido gets you
        if not delays:
            delays = []
        self.delays = delays
        self.select = select
        self.flags = flags

    def image_buffer(self) -> BytesIO:
        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        return buffer

    def meta(self) -> dict:
        meta_json = {
            "name": self.name,
            "directions": self.directions,
        }
        if self.delays:
            meta_json.update({"delays": [self.delays for _ in range(self.directions)]})
        if self.select:
            meta_json.update({"select": self.select})
        return meta_json


def meta_json_to_states(rsi_path: str) -> List[RSIState]:
    meta_json_path = os.path.join(rsi_path, "meta.json")
    with open(meta_json_path, "rb") as f:
        meta_json = json.load(f)
    rsi_states = []
    for state in meta_json.get("states", []):
        state_path = os.path.join(rsi_path, f"{state.get('name', '<blank>')}.png")
        rsi_state = RSIState(
            name=state.get("name", "<blank>"),
            data=Image.open(state_path),
            directions=state.get("directions"),
            delays=state.get("delays"),
        )
        rsi_states.append(rsi_state)

    return rsi_states


class RSI:
    # Used rsi_ prefix as license and copyright shadow built-ins
    def __init__(self,
                 data=None,
                 rsi_version: int = 1,
                 size: dict = None,
                 rsi_license: str = "CC-BY-SA-3.0",
                 rsi_copyright: str = None,
                 states: List[RSIState] = None,
                 ):

        if data is None:
            # Using mutable as arg is bad
            if size is None:
                self.size = {"x": 32, "y": 32}
            else:
                self.size = size
            self.version = rsi_version
            self.license = rsi_license
            self.copyright = rsi_copyright
            if states:
                self.states = states
            else:
                self.states = []
        elif os.path.exists(data):
            meta_json_path = os.path.join(data, "meta.json")
            with open(meta_json_path, "rb") as f:
                meta_json = json.load(f)
            self.version = meta_json.get("version")
            self.size = meta_json.get("size")
            self.license = meta_json.get("license")
            self.copyright = meta_json.get("copyright")
            self.states = meta_json_to_states(data)
        elif isinstance(data, BytesIO):
            # TODO: Use temporary directory to store .rsi instead
            pass
        else:
            raise AttributeError

    def validate_states(self):
        for state in self.states:
            if state.image.size[0] % self.size.get('x') != 0 or state.image.size[1] % self.size.get('y') != 0:
                raise InvalidRSIStateException("Dimensions for RSIState don't look valid")

        return

    def meta(self) -> dict:
        meta_json = {
            "version": self.version,
            "size": self.size,
            "license": self.license,
            "copyright": self.copyright,
            "states": [x.meta() for x in self.states if x.name],
        }
        return meta_json

    def save_to(self, path: str) -> None:
        if not path.endswith(".rsi"):
            raise AttributeError(f"path should end with .rsi")
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error(e)
                raise e
        else:
            os.mkdir(path)
            meta_path = os.path.join(path, "meta.json")
            with open(meta_path, "w") as f:
                json.dump(self.meta(), f)
            logger.info("Created meta.json")
            for state in self.states:
                if state.name:
                    state_path = os.path.join(path, f"{state.name}.png")
                    try:
                        state.image.save(state_path)
                    except ValueError as e:
                        logger.critical(f"Unable to save: state name is {state.name} and attempted file path is {state_path}")
                        raise e
                else:
                    logger.warning("No name found for state")


def _get_rsi(data):
    if isinstance(data, RSI):
        return data
    elif os.path.exists(data):
        rsi = RSI(data)
        return rsi
    else:
        raise AttributeError(f"Unable to get RSI for {type(data)}")


def combine_rsis(source, target):
    source_rsi = _get_rsi(source)
    target_rsi = _get_rsi(target)
    # TODO: Put all the states of source into target then add it to the target's metadata, then save
    raise NotImplementedError
    return


def split_rsi_states(data, new_rsis: dict, **kwargs) -> List[RSI]:
    """

    :param data: <RSI> input
    :param new_rsis: Dict of the new rsis to be made in the format {"filename": {"states": "states", **kwargs}
    :param kwargs: If any of the meta needs to be overwritten use kwargs
    :return: None
    """
    split_rsis = []
    if isinstance(data, RSI):
        data: RSI
    else:
        logger.error(f"Type {type(data)} not supported for split_rsi_states")
        AttributeError(f"Type {type(data)} not supported for split_rsi_states")

    # TODO: Performance
    for key, value in new_rsis.items():
        new_rsi = RSI(

        )
        split_rsis.append(new_rsi)
    return split_rsis