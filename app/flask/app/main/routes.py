from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
import datetime

from app import db, bcrypt
from app.models import User

main = Blueprint('main', __name__)

host = 'http://192.168.1.25:5000'

@main.route('/home', methods=['GET', 'POST'])
def home():
    motors = [1, 2, 3, 4]
    script, div, cdn_js = plot()
    return render_template('home.html', motors=motors, script=script, div=div, cdn_js=cdn_js)


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    #token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        flash('Invalid name or password', 'error')

    return render_template('login.html', title='Log in')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            flash('Username already taken!', 'error')
        elif request.form.get('password') == request.form.get('confirm_password'):
            hashed_pw = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            user = User(username=request.form.get('username'), password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash('Created new account', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('passwords must be same', 'error')

    return render_template('signup.html', title='Sign up')


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.login'))


def plot():
    from bokeh.models import AjaxDataSource, CustomJS
    from bokeh.plotting import figure
    from bokeh.resources import CDN
    from bokeh.embed import components
    from bokeh.layouts import gridplot

    pid_adapter = CustomJS(code="""
    const result = {x:[], ref:[], v:[], e:[], rv:[]}
    const pts = cb_data.response.points

    result.x.push(pts[0])
    result.ref.push(pts[1])
    result.v.push(pts[2])
    result.e.push(pts[3])
    result.rv.push(pts[4])
    return result
    """)

    pid_t_source = AjaxDataSource(data_url=f'{host}{url_for("data.get_pid_t_data")}', polling_interval=150, adapter=pid_adapter, mode='append', max_size=500)
    pid_y_source = AjaxDataSource(data_url=f'{host}{url_for("data.get_pid_y_data")}', polling_interval=250, adapter=pid_adapter, mode='append', max_size=1024)
    pid_p_source = AjaxDataSource(data_url=f'{host}{url_for("data.get_pid_p_data")}', polling_interval=250, adapter=pid_adapter, mode='append', max_size=1024)
    pid_r_source = AjaxDataSource(data_url=f'{host}{url_for("data.get_pid_r_data")}', polling_interval=250, adapter=pid_adapter, mode='append', max_size=1024)

    pid_t_plot = figure(output_backend='webgl')
    pid_y_plot = figure(output_backend='webgl')
    pid_p_plot = figure(output_backend='webgl')
    pid_r_plot = figure(output_backend='webgl')

    pid_t_plot.circle('x', 'ref', source=pid_t_source)
    pid_t_plot.circle('x', 'v', color='orange', source=pid_t_source)
    pid_t_plot.circle('x', 'rv', color='red', source=pid_t_source)

    pid_y_plot.circle('x', 'ref', source=pid_y_source)
    pid_y_plot.circle('x', 'v', color='orange', source=pid_y_source)
    pid_y_plot.circle('x', 'rv', color='red', source=pid_y_source)

    pid_p_plot.circle('x', 'ref', source=pid_p_source)
    pid_p_plot.circle('x', 'v', color='orange', source=pid_p_source)
    pid_p_plot.circle('x', 'rv', color='red', source=pid_p_source)

    pid_r_plot.circle('x', 'ref', source=pid_r_source)
    pid_r_plot.circle('x', 'v', color='orange', source=pid_r_source)
    pid_r_plot.circle('x', 'rv', color='red', source=pid_r_source)

    p = gridplot([[pid_t_plot, pid_y_plot], [pid_p_plot, pid_r_plot]])

    script, div = components(p)
    cdn_js = CDN.js_files
    return script, div, cdn_js
