
# Notes about he tmx format

Docs: https://doc.mapeditor.org/en/stable/reference/tmx-map-format/

* Tiles with `0` values have no content and should be ignored
* The stored tile id references. Subtract 1 to get the texture id
* The tile data starts from lower level corner
* Not sure what the origin of the map should be. 0, 0 at lower left corner might be correct.
