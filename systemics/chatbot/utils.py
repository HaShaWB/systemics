from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .chatObj import ChatObj


def list_to_str(list: list[str], sep: str = "\n", bullet: str = "") -> str:
    return sep.join([f"{bullet}{item}" for item in list])


def dict_to_str(dict: dict[str, str], sep: str = "\n", bullet: str = "") -> str:
    return list_to_str([f"{key}: {value}" for key, value in dict.items()], sep, bullet)

