from flask import Flask
import json
from gen_tile import get_renderers
from osgeo import ogr
import mapnik

app = Flask(__name__)

renderers = get_renderers('styles', 16)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/tiles/<layer>/<int:z>/<int:x>/<int:y>.png')
def tile_render(layer, z, x, y):
    if layer in renderers:
        cache = False
        x = renderers[layer].genTile(x, y, z, 'png', cache)
        return x, 200, {
            'Content-Type': 'image/png',
            'Cache-Control': 'max-age=300'
        } 
    else:
       return "No Renderer for " + layer, 404

@app.route('/query/<layer>/<x>/<y>')
def query(layer, x, y):
    p = mapnik.Coord(float(x),float(y))
    feats = []
    if layer in renderers:
        for l in renderers[layer].m.layers:
            for feat in l.datasource.features_at_point(p):
                feats.append(json.loads(feat.to_geojson()))
        return json.dumps(feats), 200, {
            'Content-Type': 'application/json',
            'Cache-Control': 'max-age=0'
        }
    else:
        return "No Renderer for " + layer, 404

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


if __name__ == "__main__":
    app.debug = True
    app.run()
