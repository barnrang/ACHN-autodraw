#!/usr/bin/env python3
import ast
from flask import Flask, session, redirect, url_for, request, jsonify
from flask import render_template, session, g
from werkzeug.utils import secure_filename

from PIL import Image

import serial
from time import sleep
app = Flask(__name__)
import numpy as np
from scipy.cluster.vq import kmeans
from skimage.color import rgb2hsv

ser = serial.Serial('/dev/serial0', 9600, write_timeout=2)
def send(msg, duration=0):
    print(msg)
    b_msg = '{}\r\n'.format(msg)
    ser.write(b_msg.encode('UTF-8'))
    #ser.write(b'Button A\r\n')
    sleep(duration)
    ser.write(b'RELEASE\r\n');


def send_break(msg, duration, break_time=0.1):
    send(msg, duration=duration)
    sleep(break_time)

def draw_init():
    send_break('Button X', 0.1)
    for i in range(4):
        send_break('HAT BOTTOM', 0.1)
    send_break('Button A', 0.1)
    send_break('Button L', 0.1)
    send_break('Button A', 0.1)
    send_break('Button R', 0.1)

def set_color(hue_meter, vivid_meter, bright_meter):
    send_break('Button X', 0.1)
    for i in range(5):
        send_break('HAT TOP', 0.1)
    send_break('HAT RIGHT', 0.1)
    send_break('Button A', 0.1)
    
    for hue_step, vivid_step, bright_step in zip(hue_meter, vivid_meter, bright_meter):
      #  for i in range(1):
      #      send_break('HAT LEFT', 0.1)
      #  for i in range(1):
      #      send_break('HAT RIGHT', 0.1)
      #  send_break('HAT BOTTOM', 0.1)

      #  for i in range(1):
      #      send_break('HAT LEFT', 0.1)
      #  for i in range(1):
      #      send_break('HAT RIGHT', 0.1)
      #  send_break('HAT BOTTOM', 0.1)

      #  for i in range(1):
      #      send_break('HAT LEFT', 0.1)
      #  for i in range(1):
      #      send_break('HAT RIGHT', 0.1)
      #  send_break('HAT BOTTOM', 0.1)
      #  send_break('Button R', 0.1)
        
        for i in range(30):
            send_break('HAT LEFT', 0.1)
        for i in range(hue_step):
            send_break('HAT RIGHT', 0.1)
        send_break('HAT BOTTOM', 0.1)

        for i in range(15):
            send_break('HAT LEFT', 0.1)
        for i in range(vivid_step):
            send_break('HAT RIGHT', 0.1)
        send_break('HAT BOTTOM', 0.1)

        for i in range(15):
            send_break('HAT LEFT', 0.1)
        for i in range(bright_step):
            send_break('HAT RIGHT', 0.1)
        send_break('HAT BOTTOM', 0.1)
        send_break('Button R', 0.1)

    send_break('Button A', 0.1, 2.)
    
    # Move cursor to the top left
    send_break('HAT BOTTOM', 0.1)    
    send_break('HAT LEFT', 0.1)
    send_break('Button A', 0.1)

    for i in range(16):
        send_break('HAT TOP', 0.1)
        send_break('HAT LEFT', 0.1)

    pass 

def draw_pixel(chosen_color):
    pointer = 0

    for i in range(32):
        for j in range(32):
            idx = chosen_color[i,j]
            diff = idx - pointer

            if diff == 0:
                send_break('Button A', 0.1)
                send_break('HAT RIGHT', 0.1)
                continue

            if np.abs(diff) > 8:
                if diff < 0:
                    diff += 16
                else:
                    diff -= 16

            if diff < 0:
                for k in range(np.abs(diff)):
                    send_break('Button L', 0.1)
            else:
                for k in range(diff):
                    send_break('Button R', 0.1)
            send_break('Button A', 0.1)
            pointer = idx
            send_break('HAT RIGHT', 0.1)
        send_break('HAT BOTTOM', 0.1)
        for j in range(31):
            send_break('HAT LEFT', 0.1)

    pass

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    if request.method == 'POST':
        action_to_do = request.form['request']
        send(action_to_do, 0.1)
        
    return render_template('index.html')

@app.route('/pic', methods=['POST'])
def post_picture():
    print('hello')
    if request.method == 'POST':
        if request.files:
            data = request.files['image']
            img = Image.open(request.files['image'])
            img = np.array(img)[:,:,:3]
            np.save('tmp.npy', img)
    return render_template('index.html')

@app.route('/gen-color', methods=['POST'])
def gen_color():
    img = np.load('tmp.npy')
    tech_chan_flatten = img.reshape((-1, 3))
    code, _ = kmeans(tech_chan_flatten.astype(np.float32), 15)
    #code = np.array([1,2,3])
    return jsonify(code.astype(np.uint8).tolist())

@app.route('/start-draw', methods=['POST'])
def draw_color():
    print(request.form)
    color_palette = np.array(ast.literal_eval(request.form['palette'])).astype(np.uint8)
    print('hey', color_palette)
    hsv_palette = rgb2hsv(np.expand_dims(color_palette, axis=0))[0]
    print(hsv_palette)
    hue_meter = np.around(hsv_palette[:,0] * 30).astype(np.int32)
    vivid_meter = np.around(hsv_palette[:,1] * 15).astype(np.int32)
    bright_meter = np.around(hsv_palette[:,2] * 15).astype(np.int32)
    print(hue_meter, vivid_meter, bright_meter)
    
    # Calculate color nearest
    img = np.load('tmp.npy')
    tech_chan_flatten = img.reshape((-1, 3))
    tech_chan_expand = np.expand_dims(tech_chan_flatten,axis=1).astype(np.float32)
    color_palette = np.concatenate([color_palette, [[255,255,255]]], axis=0) # Add white
    color_palette_expand = np.expand_dims(color_palette, axis=0).astype(np.float32)
    tmp = tech_chan_expand - color_palette_expand

    r = (tech_chan_expand[:,:,0] + color_palette_expand[:,:,0]) / 2
    dC = np.sqrt((2 + r / 256) * tmp[:,:,0] ** 2 + 4 * tmp[:,:,1] ** 2
                + (2+(255-r)/256)*tmp[:,:,2]**2)

    #

    chosen_color = dC.argmin(axis=1).reshape(32, 32)
    drawn_img = color_palette[chosen_color].reshape([32,32,3])
    np.save('drawn.npy', drawn_img)
    # Initial setup
    draw_init()
    set_color(hue_meter, vivid_meter, bright_meter)
    
    draw_pixel(chosen_color)

    return render_template('index.html')
#
#return 'Hello, World!'
