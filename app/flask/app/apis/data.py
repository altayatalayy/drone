from flask import Blueprint, jsonify, request
from app import r
import time

data = Blueprint('data', __name__)

@data.route('/api/data/getmotorspeed')
def get_motor_speed():
    cmd = dict(request.args)
    if not cmd:
        return jsonify(success=False), 500

    idx = int(cmd.pop('id'))
    if idx >= len(motors) or idx < 0:
        return jsonify(success=False), 500

    r.rpush('_drone_cmd', f'get_motor_speeds')
    t0 = time.time()
    while r.llen('_motor_speeds') == 0:
        time.sleep(0.05)
        t1 = time.time()
        if t1 - t0 > 2:
            return jsonify(success=False), 500
    speeds = r.lpop('_motor_speeds').decode('utf-8').split(',')#csv (e.g. '0,0,0,0')
    speeds = [int(s) for s in speeds]
    return jsonify(speed=speeds[idx])


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
    r.rpush('_drone_cmd', f'get_data')
    t0 = time.time()
    while r.llen('_data_queue') == 0:
        time.sleep(0.05)
        t1 = time.time()
        if t1 - t0 > 2:
            return jsonify(success=False), 500
    data = r.lpop('_data_queue').decode('utf-8').split(',')#csv (e.g. '0,0,0,0,0,0,0')
    data = [float(str(s)) for s in data]


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
        return jsonify(position=[x, y, z], success=True), 200
    return jsonify(success=False), 500

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
