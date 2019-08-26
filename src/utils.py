from src.dmi import DMI, DMIState
from src.rsi import RSI, RSIState
from typing import List
from requests import Session
from io import BytesIO
from logging import Logger, getLogger
from PIL import Image, ImageChops
import os


logger: Logger = getLogger(__name__)


# Ghetto: used for guns
REPO_DIRECTORY = os.path.dirname(os.path.dirname(__file__))


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
    if mode in [None, "helmets"]:
        dmi_groups += [x.name for x in dmi.states]
    if mode in ["guns", ]:
        dmi_groups += ["-".join(x.name.split("-")[0:-1]) if len(x.name.split("-")) > 1 else x.name
                        for x in dmi.states if x.name]
    if mode in ["mags", ]:
        dmi_groups += ["-".join(x.name.split("-")[0:-1]) for x in dmi.states if x.name and x.name[-1].isdigit()]
    if mode in [None, "wall"]:
        dmi_groups += [_strip_numbers(x.name) for x in dmi.states if _strip_numbers(x.name)]

    dmi_groups = set([x for x in dmi_groups if x != ""])
    icon_dmi = None
    if mode == "helmets" and kwargs.get("icons"):
        # Try and match icons as they use lower res images and are a bit more polished (rather than just resizing)
        icon_dmi = DMI(kwargs['icons'])
    for group in dmi_groups:
        logger.debug(f"Group is {group}")
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

        elif mode == "guns":
            for state in dmi.states:
                if state.name.startswith(group):
                    rsi_state = RSIState(
                        data=state.image,
                        name=state.name,
                        directions=state.dirs,
                        delays=state.delay,
                    )
                    rsi_states.append(rsi_state)
        # For this we'll be a little more strict
        elif mode == "mags":
            for state in dmi.states:
                if "".join(state.name.split("-")[0:-1]) == group:
                    rsi_state = RSIState(
                        data=state.image,
                        name=state.name,
                        directions=state.dirs,
                        delays=state.delay,
                    )
                    rsi_states.append(rsi_state)
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
        if mode == "helmets":
            if len(rsi_states) == 1:
                rsi_states[0].name = "equipped-HELMET"
                rsi_states[0].delays = [1.0]

        # If in guns / mags mode we need to get linear steps
        # TODO: Just break these out at this point
        if mode in ["guns", "mags"] and rsi_states:
            logger.info("Correcting steps")
            sorted_states = sorted(rsi_states, key=lambda x: x.name)
            # If guns: Try sorting by: Ammo account, full / empty, slide, loaded, etc.
            if mode == "guns":
                # AK, AK-20, AK-30 or saber, saber-full
                if len([x for x in sorted_states if "-" in x.name]) == len(sorted_states) - 1:
                    new_states = []
                    # First
                    new_states.append([x for x in sorted_states if "-" not in x.name][0])
                    # Rest
                    new_states.extend(sorted([x for x in sorted_states if "-" in x.name],
                                             key=lambda x:
                                             int(x.name.split("-")[-1]) if x.name.split("-")[-1].isdigit() else
                                             x.name.split("-")[-1]))
                    sorted_states = new_states
                # taser, taser0, taser25
                if len([x for x in sorted_states if "-" not in x.name and x.name[-1].isdigit()]) == \
                        len(sorted_states) - 1:
                    new_states = []
                    # First
                    new_states.extend([x for x in sorted_states if not [c for c in x.name if c.isdigit()]][0:1])
                    # Rest
                    new_states.extend(sorted([x for x in sorted_states if [c for c in x.name if c.isdigit()]],
                                             key=lambda x: "".join([c for c in x.name if c.isdigit()])))
                    sorted_states = new_states
            if mode == "mags":
                for idx, state in enumerate(sorted_states):
                    state.name = f"{group.lower()}-{idx}"
            elif mode == "guns":
                for idx, state in enumerate(sorted_states[1:]):
                    state.name = f"{group.lower()}-{idx}"
                sorted_states[0].name = group.lower()
            else:
                raise Exception
            # Also add a base state for the icon
            if mode == "mags":
                last_state = sorted_states[-1]
                sorted_states.append(RSIState(
                    data=last_state.image,
                    name=group.lower(),
                    directions=last_state.directions,
                    delays=last_state.delays,
                ))
            if mode == "guns":
                # Also need to add the old inhands
                sorted_states.extend([
                    RSIState(
                        data=os.path.join(REPO_DIRECTORY, "textures", "inhand-left.png"),
                        name="inhand-left",
                        directions=4,
                        delays=[1.0,],
                    ),
                    RSIState(
                        data=os.path.join(REPO_DIRECTORY, "textures", "inhand-right.png"),
                        name="inhand-right",
                        directions=4,
                        delays=[1.0,],
                    )
                ])
            rsi_states = sorted_states

        if mode == "helmets" and kwargs.get("icons"):
            inhand_left_image = Image.new("RGBA", size=(64, 64))
            inhand_right_image = Image.new("RGBA", size=(64, 64))
            # Get top left (facing forward) to use
            # Centered on the axis which is annoying and doesn't fit nicely into 16 x 16
            base_image_small: Image.Image = rsi_states[0].image.copy().crop(box=(9, 0, 22, 13))
            base_image_small = ImageChops.offset(base_image_small, xoffset=0, yoffset=0)
            base_image = Image.new("RGBA", size=(16, 16))

            # "Centre" it more for the below
            base_image = ImageChops.offset(base_image, xoffset=0, yoffset=2)

            base_image.paste(base_image_small, box=(1, 1, 14, 14))

            rotated = base_image.rotate(270)
            rotated_again = base_image.rotate(90)
            final_space_left_hand = ImageChops.offset(base_image, xoffset=0, yoffset=-1).rotate(90)
            final_space_right_hand = ImageChops.offset(base_image, xoffset=0, yoffset=-1).rotate(270)

            inhand_left_image.paste(ImageChops.offset(rotated, xoffset=0, yoffset=1), box=(16, 16, 32, 32))
            inhand_left_image.paste(ImageChops.offset(rotated_again, xoffset=0, yoffset=0), box=(32, 16, 48, 32))
            inhand_left_image.paste(final_space_left_hand, box=(48, 48, 64, 64))

            inhand_right_image.paste(ImageChops.offset(rotated_again, xoffset=0, yoffset=-1), box=(0, 16, 16, 32))
            inhand_right_image.paste(ImageChops.offset(rotated, xoffset=0, yoffset=0), box=(48, 16, 64, 32))
            inhand_right_image.paste(final_space_right_hand, box=(0, 48, 16, 64))

            rsi_states.append(RSIState(
                data=inhand_left_image,
                name="inhand-left",
                directions=4,
                delays=[1.0],
            ))
            rsi_states.append(RSIState(
                data=inhand_right_image,
                name="inhand-right",
                directions=4,
                delays=[1.0],
            ))

            # Try and match an icon, otherwise just resize one
            matched_icons = [x for x in icon_dmi.states if x.name == group]
            if matched_icons:
                icon_state: DMIState = matched_icons[0]
                rsi_states.append(RSIState(
                    data=icon_state.image,
                    name="icon",
                    directions=1,
                    delays=[1.0]
                ))
            else:
                icon_image: Image.Image = Image.new("RGBA", size=(32, 32))
                icon_image.paste(base_image, box=(8, 8, 24, 24))
                rsi_states.append(RSIState(
                    data=icon_image,
                    name="icon",
                    directions=1,
                    delays=[1.0]
                ))

            if len(rsi_states) == 4 and not [1 for x in rsi_states if x.name == "equipped-HELMET"]:
                for state in rsi_states:
                    if state.name not in ["icon", "inhand-left", "inhand-right"]:
                        state.name = "equipped-HELMET"
            cleanup = []
            for state in rsi_states:
                if state.name == group:
                    state.name = "equipped-HELMET"
                    state.delays = [1.0, ]
                if state.name in ["equipped-HELMET", "icon", "inhand-left", "inhand-right"]:
                    cleanup.append(state)
            rsi_states = cleanup

        if mode != "helmets" or [x for x in rsi_states if x.name == "equipped-HELMET"]:
            rsi = RSI(
                size={"x": dmi.width, "y": dmi.height},
                rsi_copyright=kwargs.get("rsi_copyright"),
                states=rsi_states,
            )
            target = os.path.join(rsi_path, f"{group.lower()}.rsi")
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


def convert_dmi_url_to_many_rsi(dmi_url: str, rsi_path: str, mode=None, **kwargs) -> None:
    icons = None
    session = Session()
    response = session.get(dmi_url)
    response.raise_for_status()
    buffer = BytesIO()  # Temporary measure as response.content doesn't seem to work
    buffer.write(response.content)
    if kwargs.get("icons"):
        icons_buffer = BytesIO()
        icon_response = session.get(kwargs['icons'])
        icon_response.raise_for_status()
        icons_buffer.write(icon_response.content)
    convert_dmi_to_many_rsi(buffer, rsi_path, rsi_copyright=dmi_url, mode=mode, icons=icons_buffer)
    return


def convert_dmi_states_to_rsi(dmi_path: str, rsi_path: str, states: List[int] = None) -> None:
    if states is None:
        raise AttributeError("Must supply states arg")

    raise NotImplementedError

# TODO: Add RSI splitter so you insert dicts of what states you want split under which name
