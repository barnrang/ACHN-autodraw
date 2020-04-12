
import serial
from time import sleep

ser = serial.Serial('/dev/serial0', 9600, write_timeout=2)

def send(msg, duration=0):
    print(msg)
    b_msg = '{}\r\n'.format(msg)
    ser.write(b_msg.encode('UTF-8'))
    #ser.write(b'Button A\r\n')
    sleep(duration)
    ser.write(b'RELEASE\r\n');

def send_break(msg, duration, break_time=0.5):
    send(msg, duration=duration)
    sleep(break_time)

send_break('Button B', 0.1)
send_break('HAT RIGHT', 0.1)
send_break('Button A', 0.1)
sleep(2)
send_break('Button A', 0.1)
sleep(0.2)
send_break('HAT TOP', 0.1)
send_break('Button A', 0.1)
