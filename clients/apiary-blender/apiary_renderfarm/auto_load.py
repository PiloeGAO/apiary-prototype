"""Auto-load addon files."""
import typing
import inspect
import pkgutil
import importlib
from pathlib import Path

import bpy
import nodeitems_utils

from apiary_renderfarm.icons import IconManager
from apiary_renderfarm.nodes import NODE_CATEGORIES
from apiary_renderfarm.panels import ApiaryEditorTree

__all__ = (
    "init",
    "register",
    "unregister",
)

blender_version = bpy.app.version

MODULES = None
ORDERED_CLASSES = None


def init():
    """Autoload initializer."""
    global MODULES  # pylint: disable=global-statement
    global ORDERED_CLASSES  # pylint: disable=global-statement

    MODULES = get_all_submodules(Path(__file__).parent)
    ORDERED_CLASSES = get_ordered_classes_to_register(MODULES)


def register():
    """Blender addon register function."""
    icon_manager = IconManager()
    icon_manager.load()

    for cls in ORDERED_CLASSES:
        bpy.utils.register_class(cls)

    for module in MODULES:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()

    bpy.types.NODE_HT_header.append(ApiaryEditorTree.draw_header)
    nodeitems_utils.register_node_categories("APIARY_NODES", NODE_CATEGORIES)


def unregister():
    """Blender addon unregister function."""
    icon_manager = IconManager()
    icon_manager.unload()

    bpy.types.NODE_HT_header.remove(ApiaryEditorTree.draw_header)
    nodeitems_utils.unregister_node_categories("APIARY_NODES")

    for cls in reversed(ORDERED_CLASSES):
        bpy.utils.unregister_class(cls)

    for module in MODULES:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()


# Import modules
#################################################


def get_all_submodules(directory):
    """Get all the python modules in a directpry.

    Args:
        directory (str): Path.

    Returns:
        list[:class:`ModuleType`]: Loaded modules.
    """
    return list(iter_submodules(directory, directory.name))


def iter_submodules(path, package_name):
    """Iterator of submodules.

    Args:
        path (str): Path.
        package_name (str): Python package name.

    Yields:
        :class:`ModuleType`: Loaded module.
    """
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)


def iter_submodule_names(path, root=""):
    """Iterator of submodules names.

    Args:
        path (str): Path.
        root (str, optional): Root package name. Defaults to "".

    Yields:
        str: Submodule python name.
    """
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################


def get_ordered_classes_to_register(modules):
    """Get ordered classes to be registred from modules.

    Args:
        modules (list[:class:`ModuleType`]): List of modules.

    Returns:
        list[class]: Ordered list of classes.
    """
    return toposort(get_register_deps_dict(modules))


def get_register_deps_dict(modules):
    """Get a dictionnary of registred dependencies of modules.

    Args:
        modules (list[:class:`ModuleType`]): List of modules.

    Returns:
        dict: Registred dependencies.
    """
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {
        cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")
    }

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(
            iter_my_register_deps(cls, my_classes, my_classes_by_idname)
        )
    return deps_dict


def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    """Iterator of registered dependency classes.

    Args:
        cls (object): Class.
        my_classes (object): List of classes.
        my_classes_by_idname (str): List of classes idnames.

    Yields:
        class: Dependency class.
    """
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)


def iter_my_deps_from_annotations(cls, my_classes):
    """Iterator for dependencies over annotations.

    Args:
        cls (object): Class.
        my_classes (object): List of classes.

    Yields:
        class: Dependency class.
    """
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency


def get_dependency_from_annotation(value):
    """Get dependency from annotation.

    Args:
        value (any): A value

    Returns:
        str: Type.
    """
    if blender_version >= (2, 93):
        if isinstance(
            value, bpy.props._PropertyDeferred
        ):  # pylint: disable=protected-access
            return value.keywords.get("type")
    else:
        if isinstance(value, tuple) and len(value) == 2:
            if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                return value[1]["type"]
    return None


def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    """Iterator over dependencies for a class based in parent idname.

    Args:
        cls (object): Class.
        my_classes_by_idname (str): Blender idname.

    Yields:
        class: Parent class.
    """
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls


def iter_my_classes(modules):
    """Iterator for classes in a module.

    Args:
        module (:class:`ModuleType`): Module.

    Yields:
        class: Class.
    """
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if not getattr(cls, "is_registered", False):
                yield cls


def get_classes_in_modules(modules):
    """Get all the classes inside of a module.

    Args:
        module (:class:`ModuleType`): Module.

    Returns:
        list[class]: Module's classes.
    """
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes


def iter_classes_in_module(module):
    """Iterator for classes inside a module.

    Args:
        module (:class:`ModuleType`): Module.

    Yields:
        class: Class.
    """
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value


def get_register_base_types():
    """Get the blender's register base types.

    Returns:
        set: Base types.
    """
    return set(
        getattr(bpy.types, name)
        for name in [
            "Panel",
            "Operator",
            "PropertyGroup",
            "AddonPreferences",
            "Header",
            "Menu",
            "Node",
            "NodeSocket",
            "NodeTree",
            "UIList",
            "RenderEngine",
            "Gizmo",
            "GizmoGroup",
        ]
    )


def toposort(deps_dict):
    """Find order to register to solve dependencies

    Args:
        deps_dict (dict): Dictionnary of dependencies.

    Returns:
        list[]: Sorted elements.
    """
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list
