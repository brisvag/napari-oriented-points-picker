from napari_plugin_engine import napari_hook_implementation

from .oriented_points_picker import oriented_points_picker


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return oriented_points_picker
