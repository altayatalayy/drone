from flask import Blueprint, jsonify, Response, url_for
from utils.data import linear

data = Blueprint('data', __name__)

l = linear()
from time import sleep
sleep(1)

@data.route('/api/data/getrotation')
def rotation():
    data = l.get_data()
    print(data)
    try:
        import math
        for i, _ in enumerate(data):
            if math.isnan(_):
                data[i] = 0
        x, y, z = data[-3:]

    except Exception as e:
        print(f'error:{e}\nmsg:{data}')
    else:
        import math
        return jsonify(position=[x, y, z])
    return jsonify(success=500), 500


import atexit

def close():
    l.close()
    print(2)

#atexit.register(close)
