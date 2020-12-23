from flask import Blueprint, jsonify, request
from app import r
import time

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


@data.route('/api/data/getrotation')
def rotation():
    data = c.get_rotation()
    if data == -1:
        return jsonify(success=False), 500
    try:
        import math
        for i, _ in enumerate(data):
            if math.isnan(_):
                data[i] = 0
        x, y, z = data

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

'''
from itertools import count
ct = count()
cy = count()
cp = count()
cr = count()
'''

@data.route('/api/data/getpidtdata', methods=['GET', 'POST'])
def get_pid_t_data():
    data = c.get_pid_t_data()
    if data == -1:
        return jsonify(success=False), 500
    return jsonify(points=data, success=True), 200


@data.route('/api/data/getpidydata', methods=['GET', 'POST'])
def get_pid_y_data():
    data = c.get_pid_y_data()
    if data == -1:
        return jsonify(success=False), 500
    return jsonify(points=data, success=True), 200

@data.route('/api/data/getpidpdata', methods=['GET', 'POST'])
def get_pid_p_data():
    data = c.get_pid_p_data()
    if data == -1:
        return jsonify(success=False), 500
    return jsonify(points=data, success=True), 200

@data.route('/api/data/getpidrdata', methods=['GET', 'POST'])
def get_pid_r_data():
    data = c.get_pid_r_data()
    if data == -1:
        return jsonify(success=False), 500
    return jsonify(points=data, success=True), 200

