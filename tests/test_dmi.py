from src.dmi import (
    DMI,
)
import os
from logging import getLogger
from tempfile import TemporaryDirectory
from tests.test_fixtures import (
    existing_dmi,
    temporary_directory,
)


logger = getLogger(__name__)


def test_open_existing_dmi(existing_dmi: DMI):
    pass


def test_dmi_metadata(existing_dmi: DMI):
    assert isinstance(existing_dmi.metadata, dict) is True


def test_save_dmi_states(existing_dmi: DMI, temporary_directory: TemporaryDirectory):
    for state in existing_dmi.states:
        state_filepath = os.path.join(temporary_directory.name, f"{state.name}.png")
        state.image.save(state_filepath)
