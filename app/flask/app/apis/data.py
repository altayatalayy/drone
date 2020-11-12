from flask import Blueprint, jsonify, request
from utils.data import linear
from utils.motors import BLDC

data = Blueprint('data', __name__)

l = linear()
from time import sleep
sleep(1)

motors = BLDC.from_csv()

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
    if not cmd:
        return jsonify(success=False), 500

    idx = int(cmd.pop('id'))
    if idx >= len(motors) or idx < 0:
        return jsonify(success=False), 500

    speed = int(cmd.pop('speed'))
    if speed > 100 or speed < 0:
        return jsonify(success=False), 500

    motors[idx].set_speed(speed)
    return jsonify(success=True), 200


@data.route('/api/data/getrotation')
def rotation():
    data = l.get_data()
    try:
        import math
        for i, _ in enumerate(data):
            if math.isnan(_):
                data[i] = 0
        x, y, z = data[-3:]

    except Exception as e:
        #print(f'error:{e}\nmsg:{data}')
        pass
    else:
        import math
        return jsonify(position=[x, y, z])
    return jsonify(success=500), 500


import atexit

def close():
    l.close()
    print(2)

#atexit.register(close)
