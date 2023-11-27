"""List of nodes related classes."""
import bpy
from bpy.types import Node, NodeSocket
from nodeitems_utils import NodeCategory, NodeItem

from apiary_submitter.core.task import Task

from apiary_renderfarm.utils import split_text, compute_framerange_chunks


class TaskSocket(NodeSocket):
    """Apiary Task Socket"""

    bl_idname = "TaskSocketType"
    bl_label = "Task Socket"

    def __init__(self):
        """Class initializer."""
        self.display_shape = "CIRCLE"
        self.link_limit = 4095  # 4095 is the maximum value allowed by the Blender API.

    def draw(self, context, layout, node, text):  # pylint: disable=unused-argument
        """Socket draw function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
            layout (:class:` bpy.types.UILayout`): Blender UI layout.
            node (:clss:` bpy.types.Node`): Blender node instance.
            text (str): Socket label.
        """
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        """Socket draw color.

        Returns:
            tuple: RGBA Color.
        """
        return (0.9, 0.49, 0.14, 1.0)


class ApiaryTreeNode:
    """Mix-in class for nodes."""

    def init(self, context):  # pylint: disable=unused-argument
        """Node initializer function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
        """
        self.inputs.new("TaskSocketType", "")  # pylint: disable=no-member
        self.outputs.new("TaskSocketType", "")  # pylint: disable=no-member

    @classmethod
    def poll(cls, ntree):
        """Node poll function, used by Blender to check if the node can be added to a tree.

        Args:
            ntree (_type_): _description_

        Returns:
            bool: `True` if the node tree is an Apiary Editor, `False` otherwise.
        """
        return ntree.bl_idname == "ApiaryEditorTreeType"

    def validate_task(self):
        """Validate node inputs for task generation.

        Raises:
            NotImplementedError: Abstract class does not provide task validation.
        """
        return NotImplementedError("Abstract class does not provide task validation.")

    def generate_task(self):
        """Generate a task from a node.

        Raises:
            NotImplementedError: Abstract class does not provide task generation.
        """
        raise NotImplementedError("Abstract class does not provide task generation.")


class TaskNode(ApiaryTreeNode, Node):
    """A Task node."""

    bl_idname = "TaskNodeType"
    bl_label = "Task"
    bl_icon = "CONSOLE"

    command_prop: bpy.props.StringProperty(name="Command")
    tags_prop: bpy.props.StringProperty(name="Tags", description="Comma separated list")

    def draw_buttons(self, context, layout):  # pylint: disable=unused-argument
        """Node display.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
            layout (:class:` bpy.types.UILayout`): Blender UI layout.
        """
        layout.prop(self, "command_prop")

    def draw_buttons_ext(self, context, layout):  # pylint: disable=unused-argument
        """Sidebar display.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
            layout (:class:` bpy.types.UILayout`): Blender UI layout.
        """
        layout.prop(self, "command_prop")
        layout.prop(self, "tags_prop")

    def validate_task(self):
        """Validate the command.

        Returns:
            bool: `True` if the command is valid, `False` otherwise.
        """
        return self.command_prop != ""

    def generate_task(self):
        """Generate the command Task.

        Returns:
            list[:class:`apiary_submitter.core.task.Task`]: Task from the node.
        """
        return [
            Task(
                self.command_prop,
                name=self.label or None,
                tags=split_text(self.tags_prop),
            )
        ]


class RenderNode(ApiaryTreeNode, Node):
    """A Render node."""

    bl_idname = "RenderNodeType"
    bl_label = "Render"
    bl_icon = "OUTLINER_OB_CAMERA"

    # TODO: move frame range to a socket allowing us to connect it to other nodes.
    start_frame_prop: bpy.props.IntProperty(name="Start frame", default=0)
    end_frame_prop: bpy.props.IntProperty(name="End frame", default=0)
    chunk_size_prop: bpy.props.IntProperty(name="Chunk size", default=5, min=1)

    tags_prop: bpy.props.StringProperty(name="Tags", description="Comma separated list")

    def init(self, context):
        """Node initializer function.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
        """
        super().init(context)

        self.start_frame_prop = bpy.context.scene.frame_start
        self.end_frame_prop = bpy.context.scene.frame_end

    def draw_buttons(self, context, layout):  # pylint: disable=unused-argument
        """Node display.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
            layout (:class:` bpy.types.UILayout`): Blender UI layout.
        """
        frame_range_row = layout.row(align=True)
        frame_range_row.prop(self, "start_frame_prop", text="")
        frame_range_row.prop(self, "end_frame_prop", text="")
        frame_range_row.prop(self, "chunk_size_prop", text="")

    def draw_buttons_ext(self, context, layout):  # pylint: disable=unused-argument
        """Sidebar display.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.
            layout (:class:` bpy.types.UILayout`): Blender UI layout.
        """
        layout.prop(self, "tags_prop")

    def validate_task(self):
        """Validate the render setup.

        Returns:
            bool: `True` if the setup is valid, `False` otherwise.
        """
        return (
            bpy.data.filepath is not None
            and self.start_frame_prop <= self.end_frame_prop
            and bpy.context.scene.render.filepath is not None
            and len(str(self.start_frame_prop))
            <= str(bpy.context.scene.render.filepath).count("#")
            and len(str(self.end_frame_prop))
            <= str(bpy.context.scene.render.filepath).count("#")
        )

    def generate_task(self):
        """Generate the render Tasks from the frame range and the chunk size.

        Returns:
            list[:class:`apiary_submitter.core.task.Task`]: Task from the node.
        """
        scene_path = bpy.data.filepath
        render_tasks = []

        for chunked_framerange in compute_framerange_chunks(
            self.start_frame_prop, self.end_frame_prop, self.chunk_size_prop
        ):
            start_frame = chunked_framerange[0]
            end_frame = chunked_framerange[-1]
            command = [
                bpy.app.binary_path,
                "-b",
                scene_path,
                "-f",
                f"{start_frame}..{end_frame}",
            ]
            render_tasks.append(
                Task(
                    " ".join(command),
                    name=f"Blender Render ({start_frame}=>{end_frame})",
                    tags=split_text(self.tags_prop),
                )
            )

        return render_tasks


class ApiaryNodesCategory(NodeCategory):
    """Apiary nodes category."""

    @classmethod
    def poll(cls, context):
        """Category poll function, used by Blender to check if the category can be added to a tree.

        Args:
            context (:class:` bpy.types.Context`): Current blender context.

        Returns:
            bool: `True` if the node tree is an Apiary Editor, `False` otherwise.
        """
        return context.space_data.tree_type == "ApiaryEditorTreeType"


NODE_CATEGORIES = [
    ApiaryNodesCategory(
        "OFFICIAL_NODES",
        "Official",
        items=[
            NodeItem("TaskNodeType"),
            NodeItem("RenderNodeType"),
        ],
    )
]
