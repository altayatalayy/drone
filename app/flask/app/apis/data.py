from flask import Blueprint, jsonify, Response, url_for
from utils.data import linear

data = Blueprint('data', __name__)

l = linear()

@data.route('/api/data/getrotation')
def rotation():
    x, y, z = l.get_data()[-3:]
    return jsonify(position=[x, y, z])
