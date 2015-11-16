#!/usr/bin/python
# -*- coding:utf-8 -*-
# Created Time: Thu Nov  5 23:58:04 2015
# Purpose: A4 pm2.5 tensor
# Mail: hewr2010@gmail.com
__author__ = "Wayne Ho"

import time
import serial
import json


class A4Signal(object):
    def __init__(self, signal):
        self.legal = False
        s = [ord(x) for x in signal]
        if not (s[0] == 50 and s[1] == 61):
            print "Auth failed"
            return
        self.time = int(time.time())
        self.pm25 = s[6] * 256 + s[7]
        self.pm10 = s[8] * 256 + s[9]
        verify_sum = sum(s[:-2])
        verify_code = s[-2] * 256 + s[-1]
        if verify_sum != verify_code:
            print "Auth failed"
            return
        self.legal = True


class A4Serial(object):
    def __init__(self, limit=1000, stride=1):
        self.limit = limit
        self.stride = stride
        self.current = -1
        self.serial = []

    def add(self, signal):
        self.current = (self.current + 1) % self.stride
        if self.current == 0:
            self.serial.append(signal)
            self.serial = self.serial[:self.limit]
            self.export()

    def export(self):
        with open("data/%d.csv" % self.stride, "w") as fout:
            print >> fout, "Time, PM2.5, PM10"
            for s in self.serial:
                time_str = time.ctime(s.time)
                print >> fout, "%s,%d,%d" % (time_str, s.pm25, s.pm10)

if __name__ == "__main__":
    recs = [
        A4Serial(stride=1, limit=3600),
        A4Serial(stride=60, limit=60*24),
        A4Serial(stride=3600, limit=31),
    ]
    ser = serial.Serial("/dev/ttyUSB0", 9600)
    while True:
        a4 = A4Signal(ser.read(32))
        if a4.legal:
            print "[PM2.5] %d\t[PM10] %d" % (a4.pm25, a4.pm10)
            for rec in recs:
                rec.add(a4)

