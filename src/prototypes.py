import yaml
from typing import List
import os
from logging import Logger, getLogger
from collections import OrderedDict

logger: Logger = getLogger(__name__)


class PrototypeComponent:
    def __init__(self,
                 ptype,
                 **kwargs):
        self.ptype = ptype
        self.kwargs = kwargs

    def to_dict(self) -> dict:
        result = {"type": self.ptype}
        result.update(self.kwargs)
        return result


def dict_sort(di: dict):
    return di
    order = [
        "type",
        "parent",
        "id",
        "name",
        "description",
        "components",
    ]
    return OrderedDict(sorted(di.items(), key=lambda x: order.index(x) if x in order else len(di)))


def key_sort(li: list) -> list:
    order = [
        "type",
        "parent",
        "id",
        "name",
        "description",
        "components",
    ]
    return sorted(li, key=lambda x: order.index(x) if x in order else len(li))


class Prototype:
    def __init__(self,
                 ptype="entity",
                 parent=None,
                 id=None,
                 name=None,
                 description=None,
                 components: List[PrototypeComponent] = None,
                 **kwargs):
        self.ptype = ptype
        self.parent = parent
        self.id = id
        self.name = name
        self.description = description
        self.kwargs = kwargs
        if not components:
            components = []
        self.components = components

    def to_dict(self) -> OrderedDict:
        # Order of insertion important below
        result = {"type": self.ptype}
        if self.parent:
            result.update({"parent": self.parent})
        result.update({
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "components": [x.to_dict() for x in self.components]
        })
        result.update(self.kwargs)

        result = dict_sort(result)
        return result


def create_glove_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    components = [
        PrototypeComponent(
            ptype="Sprite",
            sprite=f"Clothing/Gloves/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=f"Clothing/Gloves/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Clothing",
            sprite=f"Clothing/Gloves/{name}.rsi",
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")]) + " gloves"
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    prototype = Prototype(
        ptype="entity",
        parent="GlovesBase",
        id=f"Gloves{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def create_hat_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    components = [
        PrototypeComponent(
            ptype="Sprite",
            sprite=f"Clothing/Head/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=f"Clothing/Head/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Clothing",
            sprite=f"Clothing/Head/{name}.rsi",
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")])
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    prototype = Prototype(
        ptype="entity",
        parent="HatBase",
        id=f"Hat{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def create_shoes_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    components = [
        PrototypeComponent(
            ptype="Sprite",
            sprite=f"Clothing/Shoes/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=f"Clothing/Shoes/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Clothing",
            sprite=f"Clothing/Shoes/{name}.rsi",
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")]) + " shoes"
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    prototype = Prototype(
        ptype="entity",
        parent="ShoesBase",
        id=f"Shoes{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def create_suit_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    components = [
        PrototypeComponent(
            ptype="Sprite",
            sprite=f"Clothing/OuterClothing/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=f"Clothing/OuterClothing/{name}.rsi",
        ),
        PrototypeComponent(
            ptype="Clothing",
            sprite=f"Clothing/OuterClothing/{name}.rsi",
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")])
    prototype_name = " ".join([x.capitalize() for x in prototype_name.split("-")])
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    pascal_name = "".join([x.capitalize() for x in pascal_name.split("-")])
    prototype = Prototype(
        ptype="entity",
        parent="OuterclothingBase",
        id=f"Outerclothing{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def create_food_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    rsi_sprite = f"Objects/Food/{name}.rsi"
    components = [
        PrototypeComponent(
            ptype="Food",
            uses=1,
            nutriment_amount=1,
        ),
        PrototypeComponent(
            ptype="Sprite",
            sprite=rsi_sprite,
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=rsi_sprite,
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")])
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    prototype = Prototype(
        ptype="entity",
        parent="FoodBase",
        id=f"Food{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def create_drink_prototype(path: str) -> Prototype:
    name = os.path.split(path)[-1].replace(".rsi", "")
    rsi_sprite = f"Objects/Food/{name}.rsi"
    components = [
        PrototypeComponent(
            ptype="Drink",
            uses=1,
            nutriment_amount=30,
        ),
        PrototypeComponent(
            ptype="Sprite",
            sprite=rsi_sprite,
        ),
        PrototypeComponent(
            ptype="Icon",
            sprite=rsi_sprite,
        ),
    ]
    prototype_name = " ".join([x.capitalize() for x in name.split("_")])
    pascal_name = "".join([x.capitalize() for x in name.split("_")])
    prototype = Prototype(
        ptype="entity",
        parent="DrinkBase",
        id=f"Drink{pascal_name}",
        name=prototype_name,
        description="",
        components=components,
    )
    return prototype


def directory_to_gloves(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_glove_prototype(rsi))

    append_to_file(prototypes, output)
    return


def directory_to_hats(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_hat_prototype(rsi))

    append_to_file(prototypes, output)
    return


def directory_to_shoes(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_shoes_prototype(rsi))

    append_to_file(prototypes, output)
    return


def directory_to_suits(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_suit_prototype(rsi))

    append_to_file(prototypes, output)
    return


def directory_to_food(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_food_prototype(rsi))

    append_to_file(prototypes, output)
    return


def directory_to_drinks(directory: str, output: str) -> None:
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory}")
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")

    prototypes: List[Prototype] = []
    for rsi in os.listdir(directory):
        prototypes.append(create_drink_prototype(rsi))

    append_to_file(prototypes, output)
    return


def append_to_file(prototypes: List[Prototype], output) -> None:
    if not os.path.isfile(output):
        raise FileNotFoundError(f"{output}")
    # Load existing
    with open(output, "rb") as f:
        existing = yaml.load(stream=f, Loader=yaml.SafeLoader)
    if not existing:
        existing = []
    for prototype in prototypes:
        existing.append(prototype.to_dict())

    # Re-add
    with open(output, "w") as f:
        yaml.dump(data=existing, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False, sort_keys=False)
    # Format it because idek how to do it with yaml
    with open(output, "r") as f:
        lines = f.readlines()
    with open(output, "w") as f:
        f.writelines([f"\n{x}" if x[0:7] == "- type:" else x for x in lines])
    return
