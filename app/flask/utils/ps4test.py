
from pyPS4Controller.controller import Controller

from controller import ControllerApi
from scipy.interpolate import interp1d
m = interp1d([32767, -32767], [-50, 50])

c = ControllerApi()


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)



    def on_L3_up(self, val):
        val = m(val)
        print(f'up:{val}')
        c.set_throttle(val)

    def on_L3_down(self, val):
        val = m(val)
        print(f'down {val}')
        c.set_throttle(val)

    def on_L2_release(self, *args):
        c.increase_gain(1.1)

    def on_R2_release(self, *args):
        c.increase_gain(0.9)#decrease gain

    def on_square_press(self):
        ''' x '''
        c.stop()

    def on_x_press(self):
        ''' o '''
        c.start()

    def on_triangle_press(self):
        ''' kare '''
        c.quit()



if __name__ == '__main__':

    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.listen()
