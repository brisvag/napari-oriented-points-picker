#!/usr/bin/env python3


import numpy as np
from napari.layers import Points
from napari.types import LayerDataTuple
from magicgui import magic_factory
from magicgui.widgets import Container, Slider

from .math import generate_matrices, matrices_to_vectors


def init_widget(self):
    """
    initialize main widget
    """
    self._points = None
    self._slot = None
    self.sliders = Container()
    self.append(self.sliders)


def update_sliders(self, n_oriented_points):
    """
    update the number of sliders to match the number of points
    """
    while len(self.sliders) - n_oriented_points > 0:
        self.sliders.pop()
    while len(self.sliders) - n_oriented_points < 0:
        slider = Slider(label='rotation', min=0, max=359)
        slider.changed.connect(lambda event: self())
        self.sliders.append(slider)
    for i, slider in enumerate(self.sliders):
        slider.label = f'{i} rot.'


@magic_factory(call_button='Re-run', auto_call=True, labels=False, widget_init=init_widget)
def oriented_points_picker(points: Points, save_as_properties: bool = False) -> LayerDataTuple:
    """
    Take as input a points layer and generate a vectors layer representing oriented points.

    Generate basis vectors from points and rotations, such that each pair of points defines
    the new z direction and rotation defines x and y (with arbitrary but non-random initialization)
    """
    # for clarity
    self = oriented_points_picker
    # if not hasattr(self, '_points'):
        # init_widget(self)
    # on layer switch update run the function
    if self._points is not points:
        self.sliders.clear()
        if self._points is not None:
            self._points.events.data.disconnect(self._slot)
        if points is not None:
            self._slot = points.events.data.connect(lambda event: self())
        self._points = points

    if points is not None:
        data = points.data
        # discard excess points
        if len(data) % 2 == 1:
            data = data[:-1]
    else:
        data = np.array([])

    update_sliders(self, len(data) / 2)

    # generate vectors
    if data.size < 2:
        vectors = np.empty((0, 2, 3))
        colors = 'white'
        matrices = np.array([])
    else:
        starts = data[::2]
        ends = data[1::2]
        rotations = [slider.value for slider in self.sliders]

        matrices = generate_matrices(starts, ends, rotations)
        vectors = matrices_to_vectors(starts, matrices)

        colors = np.tile(np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)]),
                         (len(vectors) / 3, 1))

    if save_as_properties and points is not None:
        # need to reshape cause properties complain
        points.properties['orientations'] = matrices.reshape(-1, 9)

    return (vectors,
            dict(name='result', edge_color=colors, length=25, edge_width=5),
            'vectors')
