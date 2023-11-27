"""Addons panels."""
from itertools import chain

import bpy
from bpy.types import NodeTree

from apiary_submitter.core.job import Job

from apiary_renderfarm import icons
from apiary_renderfarm.exceptions import TaskValidationError
from apiary_renderfarm.utils import split_text


class ApiaryEditorTree(NodeTree):
    """A nodal job editor for Apiary RenderFarm."""

    bl_idname = "ApiaryEditorTreeType"
    bl_label = "Apiary Editor"
    bl_icon = "URL"

    name_prop: bpy.props.StringProperty(name="Name")
    pools_prop: bpy.props.StringProperty(
        name="Pools names", description="Comma separated list"
    )
    priority_prop: bpy.props.IntProperty(name="Priority", default=500, min=0, max=999)
    tags_prop: bpy.props.StringProperty(name="Tags", description="Comma separated list")

    @staticmethod
    def draw_header(self, context):  # pylint: disable=bad-staticmethod-argument
        """Update the header of the graph editor.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
        """
        snode = context.space_data
        if snode is None:
            return

        group = snode.edit_tree
        if not group or group.bl_idname != "ApiaryEditorTreeType":
            return

        self.layout.operator("apiary.submit", icon_value=icons.get("icon"))

    def generate_job(self):
        """Generate an Apiary Job object from the graph.

        Returns:
            :class:`apiary_submitter.core.job.Job`: Job from the graph.
        """
        tasks_from_nodes = {}

        for node in self.nodes:
            if not node.validate_task():
                tasks_from_nodes[node] = None
                continue

            tasks_from_nodes[node] = node.generate_task()

        if None in list(tasks_from_nodes.values()):
            failed_validations = [
                node.name for node, task in tasks_from_nodes.items() if task is None
            ]
            raise TaskValidationError(", ".join(failed_validations))

        for link in self.links:
            parent = link.from_node
            child = link.to_node
            for parent_task in tasks_from_nodes[parent]:
                for child_task in tasks_from_nodes[child]:
                    parent_task.add_child(child_task)

        return Job(
            self.name_prop or self.name,
            pools=split_text(self.pools_prop),
            priority=self.priority_prop,
            tasks=list(chain.from_iterable(list(tasks_from_nodes.values()))),
            tags=split_text(self.tags_prop),
            metadata=None,
        )


class NODE_PT_apiary_job_properties(bpy.types.Panel):
    """Job properties panel."""

    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Group"
    bl_label = "Job Properties"

    @classmethod
    def poll(cls, context):
        """Poll function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.

        Returns:
            _type_: _description_
        """
        snode = context.space_data
        if snode is None:
            return False
        group = snode.edit_tree
        if group is None:
            return False
        if group.is_embedded_data:
            return False
        if group.bl_idname != "ApiaryEditorTreeType":
            return False
        return True

    def draw(self, context):
        """Draw function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
        """
        layout = self.layout
        snode = context.space_data
        group = snode.edit_tree
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(group, "name_prop")
        col.prop(group, "priority_prop")
        col.prop(group, "pools_prop")
        col.prop(group, "tags_prop")
