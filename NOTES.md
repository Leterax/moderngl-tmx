
# Notes about he tmx format

Docs: https://doc.mapeditor.org/en/stable/reference/tmx-map-format/

* Tiles with `0` values have no content and should be ignored
* The stored tile id references. Subtract 1 to get the texture id
* The tile data starts from lower level corner
* Not sure what the origin of the map should be. 0, 0 at lower left corner might be correct.

# Notes about the Layer-system

### Layer Types
#### Layer
* Layer is made up of chunks with a fixed size (< 256x265)
* chunks store tiles in the format `(uint8 local_coordx uint8 local_coordy, uint16 gid)`
* Layers store chunks in a moderngl buffer


* layers have a function `find_tile(properties=Mapping[string, value])` that returns any tiles from the loaded chunks 
with custom `properties` set to `value`
* Layers can be rendered with a call to `render(pos=(x, y), render_distance=r)`, 
rendering chunks up to `r` away from `pos`. This is done by Layer-subclasses
* The buffer follows this pattern: `Buffer = [Chunk_01, Chunk_02, Chunk_03, ... ]`

##### StaticLayer
* `static`, the chunks can not be changed. 
* Chunk-values are stored continuously in one buffer.
* Chunks in the Buffer are stored following this pattern: Chunk = `[uint8 x, uint8 y, uint16 gid, ... ]`

##### DynamicLayer
* `dynamic`, the chunks and tiles contained in them can be changed. 
* the maximal amount of memory needed for one chunk is always allocated `(chunk_size * chunk_size * 4bytes)`,
even if this is never reached
* Chunks can be edited by overwriting sections of the buffer: `buffer.write(chunk, offset=sizeof(chunk) * chunk_id)`
* Areas in memory that actually contain tiles are saved in a buffer, `[num_vertices, first_offset]`
* Chunks can be drawn using `render_indirect` and the buffer containing chunk memory locations.
