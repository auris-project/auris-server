#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request
from subprocess import Popen, call
import os, signal

app = Flask(__name__, static_url_path='', static_folder='html')
process = ""
running = False

@app.route("/api/start/<music>", methods=['GET'])
def start(music):
	global process, running
	if running is False:	
		process = Popen(["sudo", "/./home/ubuntu/MUSIC_DEAF/music_for_deaf/auris-controller/auris_controller.out", music], shell=False)
		running = True
		return "Start: " + music, 200
	return "Melody are running", 405 

@app.route("/api/stop", methods=['GET'])
def stop():
	#os.kill(process.pid, signal.SIGTERM)
	os.system("sudo kill %d"%(process.pid))
	global running
	call(["sudo", "/./home/ubuntu/MUSIC_DEAF/music_for_deaf/auris-controller/auris_controller.out", "off"], shell=False)
	running = False
	return "Stop!", 200

@app.route("/")
def index():
	return app.send_static_file('index.html')

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
