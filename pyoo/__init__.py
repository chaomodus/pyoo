"""PYOO: A python MOO-like verb based text adventure engine."""

from .interpret import Interpreter, PyooError, PyooVerbNotFound
from .base import verb, prepositions, normalized_preps
from .things import Thing, Container, Place, Player
