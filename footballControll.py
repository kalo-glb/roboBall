#!/bin/python

import array
import serial
import sys

control = {'LF' : '\x10', 'LB' : '\x20', 'RF' : '\x40', 'RB' : '\x80'}

ser = serial.Serial('/dev/ttyACM0', 9600)

message = control[str(sys.argv[1])] + str(sys.argv[2]) + str(sys.argv[3])

ser.write(message)

while True:
	ser.readline()
