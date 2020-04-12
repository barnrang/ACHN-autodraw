#!/usr/bin/env python3
import argparse
import serial
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

def send(msg, duration=0):
    print(msg)
    b_msg = '{}\r\n'.format(msg)
    #ser.write(bytes(msg, 'UTF-8'));
    print(b_msg.encode('UTF-8'))
    print(b'Button A\r\n')
    ser.write(b_msg.encode('UTF-8'))
    #ser.write(b'Button A\r\n')
    sleep(duration)
    ser.write(b'RELEASE\r\n');

ser = serial.Serial(args.port, 9600, write_timeout=2)

send('Button A', 0.1)
sleep(1)
send('Button A', 0.1)
sleep(1)
send('Button A', 0.1)
sleep(3)

try:
    while True:
        sleep(0.1)
        send('Button A', 0.1)
except KeyboardInterrupt:
    send('RELEASE')
    ser.close()
