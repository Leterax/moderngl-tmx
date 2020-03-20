import moderngl_tmx as tmx
import moderngl


level = tmx.load('blah.tmx')
level.render(pos=(0,0))
