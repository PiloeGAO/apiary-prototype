"""List of all the operators for the addon."""
import webbrowser

import bpy

from apiary_submitter.core.submitter import Submitter
from apiary_submitter.exceptions import SubmitException

from apiary_renderfarm.exceptions import TaskValidationError
from apiary_renderfarm.preferences import get_preferences


class OpenApiaryInterfaceOperator(bpy.types.Operator):
    """Open the web browser to the farm monitor interface."""

    bl_idname = "apiary.openinterface"
    bl_label = "Open Interface"

    def execute(self, context):
        """Operator executor function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.

        Returns:
            _type_: _description_
        """
        preferences = get_preferences(context)
        webbrowser.open_new_tab(f"{preferences.hostname}/docs")
        return {"FINISHED"}


class SubmitApiaryJobOperator(bpy.types.Operator):
    """Submit the current opened graph to the farm."""

    bl_idname = "apiary.submit"
    bl_label = "Submit"

    def execute(self, context):
        """_summary_

        Args:
            context (:class:` bpy.types.Context`): Current blender context.

        Returns:
            enum set: _description_
        """
        preferences = get_preferences(context)
        snode = context.space_data
        if snode is None:
            self.report({"ERROR"}, "Invalid space data.")
            return {"CANCELLED"}

        group = snode.edit_tree
        if not group or group.bl_idname != "ApiaryEditorTreeType":
            self.report({"ERROR"}, "Invalid node editor.")
            return {"CANCELLED"}

        submitter = Submitter()
        try:
            job = group.generate_job()
        except TaskValidationError as error:
            self.report({"ERROR_INVALID_INPUT"}, f"Task validation failed: {error}")
            return {"CANCELLED"}

        job_id = None
        try:
            job_id = submitter.submit(job)
        except SubmitException as error:
            self.report({"ERROR"}, f"Submission failed: {error}")
            return {"CANCELLED"}

        if preferences.open_ui_at_submit:
            webbrowser.open_new_tab(f"{preferences.hostname}/jobs/{job_id}")
        else:
            self.report({"INFO"}, f"Job submitted ({job_id}).")

        return {"FINISHED"}
