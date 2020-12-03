from flask import Blueprint, jsonify, request
from utils.data import linear
from utils import motor_list as motors
from utils import l

data = Blueprint('data', __name__)

@data.route('/api/data/getmotorspeed')
def get_motor_speed():
    cmd = dict(request.args)
    if not cmd:
        return jsonify(success=False), 500

    idx = int(cmd.pop('id'))
    if idx >= len(motors) or idx < 0:
        return jsonify(success=False), 500

    return jsonify(speed=motors[idx].speed)

@data.route('/api/data/setmotorspeed', methods=['GET'])
def set_motor_speed():
    cmd = dict(request.args)
    print(cmd)
    if not cmd:
        return jsonify(success=False), 500

    idx = int(cmd.pop('id'))
    if (idx >= len(motors) or idx < 0) and not idx == -1:
        print(2)
        return jsonify(success=False), 500

    speed = int(cmd.pop('speed'))
    if speed > 100 or speed < 0:
        print(3)
        return jsonify(success=False), 500

    print(4)
    try:
        if idx == -1:
            [m.set_speed(speed) for m in motors]
        else:
            motors[idx].set_speed(speed)
    except:
        print(1)
        return jsonify(success=False), 500
    else:
        return jsonify(success=True), 200


@data.route('/api/data/getrotation')
def rotation():
    data = l.get_data()
    try:
        import math
        for i, _ in enumerate(data):
            if math.isnan(_):
                data[i] = 0
        x, y, z = data[-4:-1]

    except Exception as e:
        print(f'error:{e}\nmsg:{data}')
        pass
    else:
        import math
        return jsonify(position=[x, y, z]), 200
    return jsonify(success=500), 500

@data.route('/api/data/loadmodel')
def load_model():
    from app import r
    if request.method == 'GET':
        rv = r.get('_model')
        return jsonify(model=rv, success=True), 200
    r.set('_model', reuest.data)
    return jsonify(success=True), 200

import atexit

def close():
    l.close()
    print(2)

#atexit.register(close)
