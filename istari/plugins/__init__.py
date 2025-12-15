"""Plugin system for Istari."""

from istari.plugins.base import Plugin, PluginBase
from istari.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginBase",
    "PluginRegistry",
]

