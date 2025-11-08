from typing import Final
from xpath_builder.core import Node


def E(tag: str = "*") -> Node:
    return Node(tag)


def ATTR(name: str) -> Node:
    return Node(f"@{name}")


COMMENT: Final[Node] = Node("comment()")
TEXT: Final[Node] = Node("text()")
NODE: Final[Node] = Node("node()")
STAR: Final[Node] = Node("*")
