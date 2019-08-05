from src.dmi import DMI
from src.rsi import RSI, RSIState
from typing import List
from requests import Session
from io import BytesIO
from logging import Logger, getLogger
from PIL import Image
import os


logger: Logger = getLogger(__name__)


# TODO: That DRY violation
def convert_dmi_to_rsi(dmi_data, rsi_path: str, **kwargs) -> None:
    """
    Converts source dmi file to target rsi file
    :param dmi_data: path / BytesIO of .dmi file
    :param rsi_path: path to new rsi file
    :param index: If specified will only convert that state
    :return: None
    """
    dmi = DMI(dmi_data)
    rsi_states = []
    for state in dmi.states:
        rsi_state = RSIState(
            data=state.image,
            name=state.name,
            directions=state.dirs,
            delays=state.delay,
        )
        rsi_states.append(rsi_state)
    rsi = RSI(
        size={"x": dmi.width, "y": dmi.height},
        rsi_copyright=kwargs.get("rsi_copyright"),
        states=rsi_states,
    )
    rsi.save_to(rsi_path)
    return


def _strip_numbers(string: str) -> str:
    return "".join([c for c in string if not c.isdigit() and c not in ["-"]])


def cornerise_image(original: Image.Image) -> Image.Image:
    whole_image = Image.new(mode="RGBA", size=(64, 64))
    # Each state will get split into 4 corners
    se_corner = original.copy().crop((16, 16, 32, 32))
    whole_image.paste(se_corner, box=(16, 16, 32, 32))

    nw_corner = original.copy().crop((0, 0, 16, 16))
    whole_image.paste(nw_corner, box=(32, 0, 48, 16))

    ne_corner = original.copy().crop((16, 0, 32, 16))
    whole_image.paste(ne_corner, box=(16, 32, 32, 48))

    sw_corner = original.copy().crop((0, 16, 16, 32))
    whole_image.paste(sw_corner, box=(32, 48, 48, 64))
    return whole_image


def convert_dmi_to_many_rsi(dmi_data, rsi_path: str, mode=None, **kwargs) -> None:
    """
    Converts source dmi file to many target rsi file
    WARNING: This will be far from perfect
    :param dmi_data: path / BytesIO of .dmi file
    :param rsi_path: path to new rsi file
    :param index: If specified will only convert that state
    :return: None
    """
    if not os.path.isdir(rsi_path):
        os.mkdir(rsi_path)
        logger.info(f"Created directory {rsi_path}")
    dmi = DMI(dmi_data)
    # Find probable groupings, iterate over similar states, then output.
    # Doesn't even matter if dupe because this is hacky
    # This will ignore blank stuff which means it will likely miss things with bad names
    dmi_groups = []
    if mode in [None, ]:
        dmi_groups += [x.name.split("-")[0] for x in dmi.states if x.name.split("-")[0]]
    if mode in [None, "wall"]:
        dmi_groups += [_strip_numbers(x.name) for x in dmi.states if _strip_numbers(x.name)]
    dmi_groups = set(dmi_groups)
    for group in dmi_groups:
        rsi_states = []
        if mode == "wall" and f"{group}0" in [x.name for x in dmi.states]:

            # If it's wall mode then you also need a "full" derived from <statename>0
            rsi_states.append(
                RSIState(
                    data=dmi.states[[x.name for x in dmi.states].index(f"{group}0")].image,
                    name="full",
                    directions=1,
                    delays=None,
            ))
            # state0
            rsi_states.append(
                RSIState(
                    data=cornerise_image(dmi.states[[x.name for x in dmi.states].index(f"{group}0")].image),
                    name=f"{group}0",
                    directions=4,
                    delays=None,
            ))
            # state2
            rsi_states.append(
                RSIState(
                    data=cornerise_image(dmi.states[[x.name for x in dmi.states].index(f"{group}0")].image),
                    name=f"{group}2",
                    directions=4,
                    delays=None,
                ))
            # state1
            whole_image = Image.new(mode="RGBA", size=(64, 64), color=255)
            # top, bottom, right, left
            # - top
            nw_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}14")].image
            nw_corner = nw_corner.crop(box=(0, 0, 16, 16))
            whole_image.paste(nw_corner, box=(0, 0, 16, 16))

            # - bottom
            se_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}13")].image
            se_corner = se_corner.crop(box=(16, 16, 32, 32))
            whole_image.paste(se_corner, box=(16, 16, 32, 32))

            # - right
            ne_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}11")].image
            ne_corner = ne_corner.crop(box=(16, 0, 32, 16))
            whole_image.paste(ne_corner, box=(16, 0, 32, 16))

            # - left
            sw_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}7")].image
            sw_corner = sw_corner.crop(box=(0, 16, 16, 32))
            whole_image.paste(sw_corner, box=(0, 16, 16, 32))

            rsi_states.append(RSIState(
                data=cornerise_image(whole_image),
                name=f"{group}1",
                directions=4,
                delays=None,
            ))
            rsi_states.append(RSIState(
                data=cornerise_image(whole_image),
                name=f"{group}3",
                directions=4,
                delays=None,
            ))

            # state4
            whole_image = Image.new(mode="RGBA", size=(64, 64), color=255)
            # top, bottom, right, left
            # - left
            nw_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}7")].image
            nw_corner = nw_corner.crop(box=(0, 0, 16, 16))
            whole_image.paste(nw_corner, box=(0, 0, 16, 16))

            # - right
            se_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}11")].image
            se_corner = se_corner.crop(box=(16, 16, 32, 32))
            whole_image.paste(se_corner, box=(16, 16, 32, 32))

            # - top
            ne_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}14")].image
            ne_corner = ne_corner.crop(box=(16, 0, 32, 16))
            whole_image.paste(ne_corner, box=(16, 0, 32, 16))

            # - bottom
            sw_corner: Image.Image = dmi.states[[x.name for x in dmi.states].index(f"{group}13")].image
            sw_corner = sw_corner.crop(box=(0, 16, 16, 32))
            whole_image.paste(sw_corner, box=(0, 16, 16, 32))

            rsi_states.append(RSIState(
                data=cornerise_image(whole_image),
                name=f"{group}4",
                directions=4,
                delays=None,
            ))
            rsi_states.append(RSIState(
                data=cornerise_image(whole_image),
                name=f"{group}6",
                directions=4,
                delays=None,
            ))

            # These should be different technically but eh
            # state5
            rsi_states.append(RSIState(
                data=cornerise_image(dmi.states[[x.name for x in dmi.states].index(f"{group}15")].image),
                name=f"{group}5",
                directions=4,
                delays=None,
            ))

            # state7
            rsi_states.append(RSIState(
                data=cornerise_image(dmi.states[[x.name for x in dmi.states].index(f"{group}15")].image),
                name=f"{group}7",
                directions=4,
                delays=None,
            ))
            rsi_states.sort(key=lambda x: x.name)

        else:
            for state in dmi.states:
                if state.name.startswith(group):
                    rsi_state = RSIState(
                        data=state.image,
                        name=state.name,
                        directions=state.dirs,
                        delays=state.delay,
                    )
                    rsi_states.append(rsi_state)
        rsi = RSI(
            size={"x": dmi.width, "y": dmi.height},
            rsi_copyright=kwargs.get("rsi_copyright"),
            states=rsi_states,
        )
        target = os.path.join(rsi_path, f"{group}.rsi")
        logger.info(f"Saved rsi to {target}")
        rsi.save_to(target)
    return


# TODO: Add some sort of buffer loader via BytesIO to avoid doing this shit. Will require editing the normal classes
def convert_dmi_url_to_rsi(dmi_url: str, rsi_path: str) -> None:
    session = Session()
    response = session.get(dmi_url)
    response.raise_for_status()
    buffer = BytesIO()  # Temporary measure as response.content doesn't seem to work
    buffer.write(response.content)
    convert_dmi_to_rsi(buffer, rsi_path, rsi_copyright=dmi_url)
    return


def convert_dmi_url_to_many_rsi(dmi_url: str, rsi_path: str, mode=None) -> None:
    session = Session()
    response = session.get(dmi_url)
    response.raise_for_status()
    buffer = BytesIO()  # Temporary measure as response.content doesn't seem to work
    buffer.write(response.content)
    convert_dmi_to_many_rsi(buffer, rsi_path, rsi_copyright=dmi_url, mode=mode)
    return


def convert_dmi_states_to_rsi(dmi_path: str, rsi_path: str, states: List[int] = None) -> None:
    if states is None:
        raise AttributeError("Must supply states arg")

    raise NotImplementedError

# TODO: Add RSI splitter so you insert dicts of what states you want split under which name
