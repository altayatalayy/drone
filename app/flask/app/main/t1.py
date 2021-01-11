host = '192.168.1.23:5000'

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

    pid_t_source = AjaxDataSource(data_url=f'{host}', polling_interval=100, adapter=pid_adapter, mode='append', max_size=500)
    pid_y_source = AjaxDataSource(data_url=f'{host}', polling_interval=100, adapter=pid_adapter, mode='append', max_size=1024)
    pid_p_source = AjaxDataSource(data_url=f'{host}', polling_interval=100, adapter=pid_adapter, mode='append', max_size=1024)
    pid_r_source = AjaxDataSource(data_url=f'{host}', polling_interval=100, adapter=pid_adapter, mode='append', max_size=1024)

    pid_t_plot = figure(title='dist', output_backend='webgl')
    pid_y_plot = figure(title='yaw', output_backend='webgl')
    pid_p_plot = figure(title='pitch', output_backend='webgl')
    pid_r_plot = figure(title='roll', output_backend='webgl')

    pid_t_plot.line('x', 'ref',  legend_label="ref", source=pid_t_source)
    pid_t_plot.line('x', 'v', color='orange',  legend_label="measured", source=pid_t_source)
    pid_t_plot.line('x', 'rv', color='red',  legend_label="pid out", source=pid_t_source)

    pid_y_plot.line('x', 'ref', source=pid_y_source)
    pid_y_plot.line('x', 'v', color='orange', source=pid_y_source)
    pid_y_plot.line('x', 'rv', color='red', source=pid_y_source)

    pid_p_plot.line('x', 'ref', source=pid_p_source)
    pid_p_plot.line('x', 'v', color='orange', source=pid_p_source)
    pid_p_plot.line('x', 'rv', color='red', source=pid_p_source)

    pid_r_plot.line('x', 'ref', source=pid_r_source)
    pid_r_plot.line('x', 'v', color='orange', source=pid_r_source)
    pid_r_plot.line('x', 'rv', color='red', source=pid_r_source)

    p = gridplot([[pid_t_plot, pid_y_plot], [pid_p_plot, pid_r_plot]])

    script, div = components(p)
    cdn_js = CDN.js_files
    return script, div, cdn_js


script, div, cdn_js = plot()

import redis
r = redis.Redis('localhost')

