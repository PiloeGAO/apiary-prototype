"""Addon's icons management."""
import os

import bpy
import bpy.utils.previews

IMAGES_EXT = [
    ".png",
    ".svg",
]


def get(name):
    """Get an icon ID from the manager.

    Args:
        name (str): Icon name.

    Returns:
        int: Icon ID.
    """
    icon_manager = IconManager()
    try:
        icon = icon_manager.previews[name]
    except TypeError:
        print(f"Failed to get the desired icon: {name}")
        return None

    return icon.icon_id


class IconManager(object):
    """A signleton icon manager."""

    _instance = None

    previews = None

    def __new__(cls):
        """Singleton loader.

        Returns:
            :class:`IconManager`: IconManager instance.
        """
        if not cls._instance:
            cls._instance = super(IconManager, cls).__new__(cls)

        return cls._instance

    def load(self):
        """Load all the icons."""
        preview_collection = bpy.utils.previews.new()
        for element in os.scandir(os.path.dirname(__file__)):
            element_name, element_extension = os.path.splitext(element.name)
            if not element.is_file() or not element_extension in IMAGES_EXT:
                continue

            preview_collection.load(element_name, element.path, "IMAGE")

        self.previews = preview_collection

    def unload(self):
        """Unload the icons."""
        bpy.utils.previews.remove(self.previews)
        self.previews = None
