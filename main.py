#!/usr/bin/python
# -*- coding:utf-8 -*-
# Created Time: Thu Nov  5 23:58:04 2015
# Purpose: A4 pm2.5 tensor
# Mail: hewr2010@gmail.com
__author__ = "Wayne Ho"

import time
import serial
#import matplotlib.pyplot as plt


class A4Signal(object):
    def __init__(self, signal):
        s = [ord(x) for x in signal]
        assert s[0] == 50 and s[1] == 61
        self.pm25 = s[6] * 256 + s[7]
        self.pm10 = s[8] * 256 + s[9]
        verify_sum = sum(s[:-2])
        verify_code = s[-2] * 256 + s[-1]
        if verify_sum != verify_code:
		print "Auth failed"


class A4Serial(object):
    def __init__(self, limit=20, level=150):
        self.limit = limit
        self.level = level
        self.serial = []
#        plt.ion()
#        plt.show()

    def add(self, signal):
        self.serial.append(signal)
        self.serial = self.serial[:self.limit]
        v25 = [a4.pm25 for a4 in self.serial]
        v10 = [a4.pm10 for a4 in self.serial]
        max_val = max(v25 + v10)
#        plt.clf()
#        plt.xlim(0, self.limit)
#        plt.ylim(0, max(self.level, max_val))
#        plt.plot(v25, label="pm2.5")
#        plt.legend()
#        plt.plot(v10, label="pm10")
#        plt.legend()
#        plt.draw()

if __name__ == "__main__":
    serial_recorder = A4Serial()
    ser = serial.Serial("/dev/ttyUSB0", 9600)
    while True:
        a4 = A4Signal(ser.read(32))
        print "[PM2.5] %d\t[PM10] %d" % (a4.pm25, a4.pm10)
        serial_recorder.add(a4)
