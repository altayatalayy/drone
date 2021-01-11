from flask import Blueprint, jsonify, request
from app import r
import time
import math

data = Blueprint('data', __name__)

from utils.controller import ControllerApi
c = ControllerApi()

@data.route('/api/data/getmotorspeed')
def get_motor_speed():
    cmd = dict(request.args)
    if not cmd:
        return jsonify(success=False), 500

    idx = int(cmd.pop('id'))
    if idx >= len(motors) or idx < 0:
        return jsonify(success=False), 500

    speeds = c.get_motor_speeds()
    if speeds == -1:
        return jsonify(success=False), 500
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

@data.route('/api/data/setcontroller', methods=['GET', 'POST'])
def set_controller():
    cmd = dict(request.args)
    if not cmd:
        return jsonify(success=False), 500
    state = int(cmd.pop('state'))
    if state:
        c.start()
    else:
        c.stop()

    return jsonify(success=True), 200

@data.route('/api/data/getrotation')
def rotation():
    data = c.get_rotation()
    if data == -1:
        return jsonify(success=False), 500
    try:
        for i, _ in enumerate(data):
            if math.isnan(_):
                data[i] = 0
        x, y, z = data

    except Exception as e:
        print(f'error:{e}\nmsg:{data}')
        pass
    else:
        return jsonify(position=[math.radians(x), math.radians(y), math.radians(z)], success=True), 200
    return jsonify(success=False), 500

@data.route('/api/data/loadmodel')
def load_model():
    from app import r
    if request.method == 'GET':
        rv = r.get('_model')
        return jsonify(model=rv, success=True), 200
    r.set('_model', reuest.data)
    return jsonify(success=True), 200

@data.route('/api/data/getpidtdata', methods=['GET', 'POST'])
def get_pid_t_data():
    n = 5
    rv = [None for  _ in range(n)]
    for i in range(n):
        data = c.get_pid_t_data()
        if data == -1:
            return jsonify(success=False), 500
        rv[i] = data
        time.sleep(0.1)
    return jsonify(points=rv, success=True), 200


@data.route('/api/data/getpidydata', methods=['GET', 'POST'])
def get_pid_y_data():
    n = 5
    rv = [None for _ in range(n)]
    for i in range(n):
        data = c.get_pid_y_data()
        if data == -1:
            return jsonify(success=False), 500
        rv[i] = data
        time.sleep(0.1)
    return jsonify(points=rv, success=True), 200

@data.route('/api/data/getpidpdata', methods=['GET', 'POST'])
def get_pid_p_data():
    n = 20
    rv = [None for _ in range(n-2)]
    for i in range(n-2):
        data = c.get_pid_p_data()
        if data == -1:
            return jsonify(success=False), 500
        rv[i] = data
        time.sleep(0.55/n)
    return jsonify(points=rv, success=True), 200

@data.route('/api/data/getpidrdata', methods=['GET', 'POST'])
def get_pid_r_data():
    n = 20
    rv = [None for _ in range(n-2)]
    for i in range(n-2):
        data = c.get_pid_r_data()
        if data == -1:
            return jsonify(success=False), 500
        rv[i] = data
        time.sleep(0.55/n)
    #print(rv)
    return jsonify(points=rv, success=True), 200

