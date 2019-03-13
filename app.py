from flask import Flask, jsonify
from qloo import *
app = Flask(__name__)
# allows use of lists with syntax /Artist+Artist+Artist/
from util import ListConverter
app.url_map.converters['list'] = ListConverter

@app.route('/')
def index():
    return 'Index Page'

@app.route('/qloo/<list:artists>/<longitude>/<latitude>/<radius>')
def qloo(artists, longitude, latitude, radius):
    print(artists)
    return jsonify(get_qloo(artists, longitude + ',' + latitude, radius))


if __name__ == '__main__':
    app.run()
