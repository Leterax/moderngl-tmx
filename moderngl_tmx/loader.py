from pathlib import Path
from typing import List, Tuple

from PIL import Image
import numpy as np
import pytiled_parser
import moderngl
from pytiled_parser.objects import Layer, ObjectLayer, TileLayer, TileMap

vertex_shader = """
#version 330
in vec2 in_position;
in int gid;
uniform vec2 pos;
out int vs_gid;

void main() {
    gl_Position = vec4(in_position + pos, 0., 1.0);
    vs_gid = gid;
}"""
geometry_shader = """
#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

in int vs_gid[1];

uniform float size;
uniform mat4 projection;

out vec2 uv;
flat out int gid;

void main() {
    vec2 pos =  gl_in[0].gl_Position.xy;
    vec2 right = vec2(1.0, 0.0) * size / 2;
    vec2 up = vec2(0.0, 1.0) * size / 2;

    uv = vec2(1.0, 1.0);
    gid = vs_gid[0];
    gl_Position = projection * vec4(pos + (right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 1.0);
    gid = vs_gid[0];
    gl_Position = projection * vec4(pos + (-right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(1.0, 0.0);
    gid = vs_gid[0];
    gl_Position = projection * vec4(pos + (right - up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 0.0);
    gid = vs_gid[0];
    gl_Position = projection * vec4(pos + (-right - up), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
"""
fragment_shader = """
#version 330
out vec4 fragColor;
in vec2 uv;
flat in int gid;

uniform sampler2DArray texture0;

void main() {
    fragColor = texture(texture0, vec3(uv, gid));
}
"""


class TileMapVAO:
    def __init__(self, layer_vaos: List[moderngl.VertexArray], texture_array: moderngl.TextureArray):
        self._layer_VAOs = layer_vaos
        self._texture_array = texture_array

    def render_layer(self, layer_id: int, projection, pos: Tuple[int, int] = (0, 0),
                     advance_animation: bool = False) -> None:
        vao = self._layer_VAOs[layer_id]
        vao.program["pos"].value = pos
        vao.program["projection"].write(projection)
        if advance_animation:
            vao.program["animation"] += 1

        vao.render(mode=moderngl.POINTS)

    def render_all(self, projection, pos: Tuple[int, int] = (0, 0), advance_animation: bool = False) -> None:
        for vao in self._layer_VAOs:
            vao.program["pos"].value = pos
            vao.program["projection"].write(projection)
            if advance_animation:
                vao.program["animation"] += 1

            vao.render(mode=moderngl.POINTS)


def load_level(level_path: Path, ctx: moderngl.context) -> TileMapVAO:
    # load the level from the file
    tile_map = pytiled_parser.parse_tile_map(level_path)

    # create the texture array for looking up the textures
    # find the tile_set with the largest offset
    max_tile_set_offset = max(tile_map.tile_sets.keys())
    # find the max tile of that tile_set
    num_layers = max_tile_set_offset + max(tile_map.tile_sets[max_tile_set_offset].tiles.keys())

    # stack all images into one large numpy array
    image_paths = []
    for gid in range(1, num_layers + 1):
        image = pytiled_parser.utilities.get_tile_by_gid(gid, tile_map.tile_sets).image
        path = level_path.parent / image.source
        image_paths.append(path)

    images = [Image.open(image_path).resize(tile_map.tile_size).convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM) for
              image_path in image_paths]
    combined_image = np.vstack((np.asarray(i) for i in images))

    # Quick test displaying the generated texture array with pillow
    # test = Image.frombuffer('RGBA', (tile_map.tile_size[0], tile_map.tile_size[1] * num_layers), combined_image)
    # test.show()

    # create the texture array
    texture_array = ctx.texture_array((*tile_map.tile_size, num_layers), 4, combined_image)
    texture_array.repeat_x = False
    texture_array.repeat_y = False
    texture_array.build_mipmaps()
    texture_array.filter = moderngl.LINEAR, moderngl.LINEAR_MIPMAP_LINEAR
    texture_array.use(0)
    # create a list of vaos; one for each layer
    vaos = [_create_vao(layer_id, tile_map, ctx) for layer_id in range(len(tile_map.layers))]
    return TileMapVAO(vaos, texture_array)


def _create_vao(layer_id: int, tile_map: TileMap, ctx):
    layer: Layer = tile_map.layers[layer_id]
    program = ctx.program(vertex_shader=vertex_shader,
                          geometry_shader=geometry_shader,
                          fragment_shader=fragment_shader
                          )
    program['texture0'] = 0
    program['size'] = float(tile_map.tile_size.width)

    if type(layer) is ObjectLayer:
        layer: ObjectLayer
        pos = []
        ids = []
        for tiled_object in layer.tiled_objects:
            pos.append(tiled_object.location)
            ids.append(tiled_object.gid)

        pos_buffer = ctx.buffer(np.array(pos, dtype=np.float32))
        id_buffer = ctx.buffer(np.array(ids, dtype=np.int32))
        vao = ctx.vertex_array(
            program, [
                (pos_buffer, '2f4', 'in_position'),
                (id_buffer, 'i', 'gid')
            ]
        )
        return vao

    elif type(layer) is TileLayer:
        layer: TileLayer
        pos = []
        ids = []
        for y in range(layer.size.height):
            for x in range(layer.size.width):
                # Empty tiles have 0 value
                if layer.data[y][x] > 0:
                    pos.append((
                        x * tile_map.tile_size.width + tile_map.tile_size.width // 2,
                        y * -tile_map.tile_size.height - tile_map.tile_size.height // 2 + tile_map.tile_size.height * layer.size.height
                    ))
                    ids.append(layer.data[y][x] - 1)

        pos_buffer = ctx.buffer(np.array(pos, dtype=np.float32))
        id_buffer = ctx.buffer(np.array(ids, dtype=np.int32))

        vao = ctx.vertex_array(
            program, [
                (pos_buffer, '2f', 'in_position'),
                (id_buffer, 'i', 'gid')
            ]
        )
        return vao
