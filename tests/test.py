from pathlib import Path

import moderngl_window as mglw
from pyrr import Matrix44
import numpy as np

import moderngl_tmx as tmx


class Test(mglw.WindowConfig):
    # moderngl_window settings
    gl_version = (4, 3)
    title = "test"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 4

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.proj = Matrix44.orthogonal_projection(0, self.wnd.buffer_width, 0, self.wnd.buffer_height, 1.0, 10.0,
                                                   dtype='f4')
        translation = Matrix44.from_translation(np.array([0, 0, 10]), dtype='f4')
        self.proj = translation * self.proj

        self.level = tmx.load_level(self.resource_dir / 'examples/arcade_example' / 'map.tmx',
                                    chunk_size=(16, 16), ctx=self.ctx)

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.clear()

        # just render one of the layers
        self.level.render_layer(layer_id=1, pos=(0, 0), advance_animation=False, matrix=self.proj)
        # render all layers above each other
        # self.level.render_all(pos=(0, 0), advance_animation=False)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(Test)
