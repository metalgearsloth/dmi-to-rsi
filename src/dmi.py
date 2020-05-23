from logging import Logger, getLogger
from PIL import Image
from src.internal_utils import handle_data_to_pil_image
from math import sqrt, ceil

logger: Logger = getLogger(__name__)


class InvalidMetadataException(Exception):
    pass


# TODO: Add tests for all of the below and in the other files


def is_png(png_bytes: bytes) -> bool:
    if png_bytes[1:4] == b'PNG':
        return True
    else:
        return False


def validate_dmi(png_bytes: bytes) -> None:
    if not is_png(png_bytes):
        raise AttributeError
    return


class DMI:
    def __init__(self,
                 data,
                 ):
        """
        Class of a byond .dmi file
        :param data: path / BytesIO of .dmi. Thankfully we can extract all the data from its metadata
        :param index: Specifies one item to pull out as a state
        """
        self.image = handle_data_to_pil_image(data)
        # Once we get self.image we're golden
        self.states = None
        self.metadata = self._parse_metadata()
        self.states = []
        index = 0
        for state in self.metadata.get("states"):
            dmi_image = dmi_state_images(self.image, index, frames=state.get("frames"), directions=state.get("dirs"))
            index += state.get("frames", 0) * state.get("dirs", 1)
            self.states.append(DMIState(metadata=state, image=dmi_image))

    @property
    def width(self) -> int:
        return self.metadata.get("width")

    @property
    def height(self) -> int:
        return self.metadata.get("height")

    def _process_file(self):
        pass

    def _parse_metadata(self):
        # PyYaml was giving me the shits so custom parse - famous last words
        base_metadata: str = self.image.info.get("Description")
        split_metadata = base_metadata.splitlines()
        # Start row is # BEGIN DMI and end row is # END DMI
        # Parse version etc first
        output = {
            "version": split_metadata[1].split(" = ")[1],
            "width": int(split_metadata[2].split(" = ")[1]),
            "height": int(split_metadata[2].split(" = ")[1]),
            "states": []
        }
        for line in base_metadata.splitlines()[4:-1]:
            # Should only be raised if coding is bad, which it is
            if len(line.split(" = ")) > 2:
                logger.critical("Unable to parse metadata for .dmi")
                raise InvalidMetadataException("Unable to parse metadata for .dmi")
            # version and state
            elif line[0] != "\t":
                description = line.split(" = ")[-1].replace('"', "")
                output["states"].append({"name": description})
            else:
                description = line.split(" = ")[0][1:]
                value = line.split(" = ")[1]
                # width / height / dirs / frames
                if len(value) == len([c for c in value if c.isdigit()]):
                    value = int(value)
                elif "," in value:
                    value = [float(d) for d in value.split(",")]
                else:
                    logger.critical(f"Unable to find value format for {value}")
                    raise InvalidMetadataException(f"Unable to find value format for {value}")

                if description == "delay":
                    value = [x / 10 for x in value]

                output["states"][-1].update({description: value})

        return output


def dmi_state_images(image: Image.Image, index: int, frames: int, directions: int = 1, size: tuple = (32, 32)) \
        -> Image.Image:
    image_columns = int(image.width / size[0])
    image_count = frames * directions
    # TODO: Verify image size
    individual_frames = []
    for i in range(index, index + image_count):
        # Get square
        start_x = i % image_columns
        start_y = int(i / image_columns)
        box = (
            start_x * size[0],
            start_y * size[1],
            (start_x * size[0]) + size[0],
            (start_y * size[1]) + size[1],
        )
        cropped_image = image.crop(box)
        individual_frames.append(cropped_image)
    column_count = ceil(sqrt(image_count))
    target_image_size = (column_count * size[0], ceil(image_count / column_count) * size[1])
    target_image = Image.new("RGBA", size=target_image_size)
    for idx, frame in enumerate(individual_frames):
        box = (
            (idx * size[0]) % target_image_size[0],
            int(idx / target_image_size[0] * size[1]) * size[1],
            (idx * size[0]) % target_image_size[0] + size[0],
            int(idx / target_image_size[0] * size[1]) * size[1] + size[1],
        )
        # This here mainly if I'm being dumb
        if box[1] > target_image_size[0]:
            logger.critical(f"Target X {box[1]} outside bounds of image {target_image_size[0]}")
            raise ValueError(f"Target X {box[1]} outside bounds of image {target_image_size[0]}")
        if box[3] > target_image_size[1]:
            logger.critical(f"Target Y {box[3]} outside bounds of image {target_image_size[1]}")
            raise ValueError(f"Target Y {box[3]} outside bounds of image {target_image_size[1]}")
        target_image.paste(frame, box)

    return target_image


class DMIState:
    def __init__(self,
                 metadata: dict = None,
                 image: Image.Image = None,
                 ):
        if metadata:
            self.name = metadata.get("name")
            self.dirs = metadata.get("dirs")
            self.frames = metadata.get("frames")
            self.delay = metadata.get("delay")
            self.image = image
        else:
            logger.critical(f"No metadata provided for DMIState")
            raise AttributeError
