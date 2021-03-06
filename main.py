#!/usr/bin/python
# -*- coding:utf-8 -*-
# Created Time: Thu Nov  5 23:58:04 2015
# Purpose: A4 pm2.5 tensor
# Mail: hewr2010@gmail.com
__author__ = "Wayne Ho"

import time
import serial
import json
import os
import csv


class A4Signal(object):
    def __init__(self, signal=None):
        if signal is None:
            return
        self.legal = False
        s = [ord(x) for x in signal]
        if not (s[0] == 50 and s[1] == 61):
            print "Auth failed"
            return
        self.time = int(time.time())
        self.pm1  = s[4] * 256 + s[5]
        self.pm25 = s[6] * 256 + s[7]
        self.pm10 = s[8] * 256 + s[9]
        verify_sum = sum(s[:-2])
        verify_code = s[-2] * 256 + s[-1]
        if verify_sum != verify_code:
            print "Auth failed"
            return
        self.legal = True

    def set_value(self, _time, pm1, pm25, pm10):
        self.time = _time
        self.pm1 = pm1
        self.pm25 = pm25
        self.pm10 = pm10
        self.legal = True


class A4Serial(object):
    def __init__(self, limit=1000, stride=1):
        self.limit = limit
        self.stride = stride
        self.current = -1
        self.serial = []
        self.path = "data/%d.csv" % stride
        if os.path.exists(self.path):
            for idx, arr in enumerate(csv.reader(open(self.path))):
                if idx > 0:
                    sig = A4Signal()
                    timestamp = time.mktime(time.strptime(arr[0]))
                    sig.set_value(timestamp, int(arr[1]), int(arr[2]), int(arr[3]))
                    self.serial.append(sig)

    def add(self, signal):
        self.current = (self.current + 1) % self.stride
        if self.current == 0:
            self.serial.append(signal)
            while len(self.serial) > self.limit:
                self.serial.pop(0)
            self.export()

    def export(self):
        with open(self.path, "w") as fout:
            print >> fout, "Time, PM1, PM2.5, PM10"
            for s in self.serial:
                time_str = time.ctime(s.time)
                print >> fout, "%s,%d,%d,%d" % (time_str, s.pm1, s.pm25, s.pm10)

if __name__ == "__main__":
    recs = [
        A4Serial(stride=5, limit=60 * 10 / 5),
        A4Serial(stride=60, limit=60),
        A4Serial(stride=3600, limit=24),
    ]
    ser = serial.Serial("/dev/ttyUSB0", 9600)
    while True:
        a4 = A4Signal(ser.read(32))
        if a4.legal:
            print "[PM1] %d\t[PM2.5] %d\t[PM10] %d" % (a4.pm1, a4.pm25, a4.pm10)
            for rec in recs:
                rec.add(a4)

