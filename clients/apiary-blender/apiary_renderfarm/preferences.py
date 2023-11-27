"""Addon's preferences."""
import os

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty

from apiary_renderfarm import icons


def get_preferences(context):
    """Get the preferences for the addon.

    Args:
        context (:class:` bpy.types.Context`): Current blender context.

    Returns:
        :class:`bpy.types.AddonPreferences`: Apiary preferences.
    """
    return context.preferences.addons[__package__].preferences


class ApiaryPreferences(AddonPreferences):
    """Addon preferences."""

    bl_idname = __package__

    hostname: StringProperty(
        name="Host name", default=os.environ.get("APIARY_HOST", "")
    )

    open_ui_at_submit: BoolProperty(
        name="Open the interface after a submission", default=True
    )

    def draw(self, context):  # pylint: disable=unused-argument
        """Draw the preferences.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
        """
        layout = self.layout
        host_row = layout.row(align=True)
        host_row.prop(self, "hostname", expand=True)
        host_row.operator("apiary.openinterface", text="", icon_value=icons.get("icon"))

        layout.prop(self, "open_ui_at_submit")
