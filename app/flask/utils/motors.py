# This program will let you test your ESC and brushless motor.
# Make sure your battery is not connected if you are going to calibrate it at first.
# Since you are testing your motor, I hope you don't have your propeller attached to it otherwise you are in trouble my friend...?
# This program is made by AGT @instructable.com. DO NOT REPUBLISH THIS PROGRAM... actually the program itself is harmful                                             pssst Its not, its safe.

import os
import time
import pigpio #importing GPIO library, service pigpiod has to be running

class BLDC:
    pi = pigpio.pi()
    max_value = 2000
    min_value = 1000

    def __init__(self, pin_num):
        self.pin = pin_num
        self.speed = 0

    @staticmethod
    def from_csv(file_name='./pins.csv'):
        import csv
        with open(file_name, 'r') as f:
            rv = []
            for i, pin_num, *meta in enumerate(csv.reader(f, delimiter=',')):
                try:
                    pin_num = int(pin_num[0])
                except ValueError as e:
                    print(e)
                except IndexError as e:
                    print(e)
                else:
                    rv.append(BLDC(pin_num, *meta))
        return tuple(rv)


    def set_speed(self, speed:'int:percentage'):
        if not (speed >= 0 and speed <= 100) and not speed == -100:
            raise ValueError(f'speed must be an int betwenn -100 and 100')
        self.speed = int(self.min_value + (self.max_value - self.min_value) * (speed / 100))
        self.pi.set_servo_pulsewidth(self.pin, self.speed)

    def get_speed(self):
        return int((self.speed - self.min_value) / (self.max_value - self.min_value))

    def calibrate(self):   #This is the auto calibration procedure of a normal ESC
        self.set_speed(0)
        print("Disconnect the battery and press Enter")
        inp = input()
        if inp == '':
            self.set_speed(100)
            print("Connect the battery NOW.. you will here two beeps, then wait for a gradual falling tone then press Enter")
            inp = input()
            if inp == '':
                self.set_speed(0)
                print("Wierd eh! Special tone")
                time.sleep(7)
                print("Wait for it ....")
                time.sleep (5)
                print("Im working on it, DONT WORRY JUST WAIT.....")
                self.set_speed(-100)
                time.sleep(2)
                print("Arming ESC now...")
                self.set_speed(0)
                time.sleep(1)

    def arm(self): #This is the arming procedure of an ESC
        print("Connect the battery and press Enter")
        inp = input()
        if inp == '':
            self.set_speed(-100)
            time.sleep(1)
            self.set_speed(100)
            time.sleep(1)
            self.set_speed(0)
            time.sleep(1)

    def stop(self): #This will stop every action your Pi is performing for ESC ofcourse.
        self.set_speed(-100)
        self.pi.stop()

if __name__ == '__main__':
    import argparse

