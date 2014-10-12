from flask import Flask
from gen_tile import get_renderers

app = Flask(__name__)

renderers = get_renderers('styles', 16)
print renderers

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/tiles/<layer>/<int:z>/<int:x>/<int:y>.png')
def tile_render(layer, z, x, y):
    if layer in renderers:
        cache = False
        x = renderers[layer].genTile(x, y, z, 'png', cache)
        return x, 200, {'Content-Type': 'image/png'} 
    else:
       return "No Renderer for " + layer, 404

if __name__ == "__main__":
    app.debug = True
    app.run()
