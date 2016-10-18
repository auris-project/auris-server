#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request
import os
import socket

app = Flask(__name__, static_url_path='', static_folder='html')
ip = '192.168.0.105'
port = 3300
buffersize = 1024
message = "write"
ponto_de_parada = "*"
start2 = "start"
stop2 = "stop"

path = "/home/luzenildo/MUSIC_DEAF/music_for_deaf_files/auris_melodies/musica.txt"

@app.route("/api/arduino-post", methods=['GET'])
def post_arduino():
	work_file = open(path, "rb")
	file_size = str(os.stat(path).st_size)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	#s.send(message)
	#data = s.recv(BUFFER_SIZE)
	print "sending file"
	file_size = int(file_size)
	#while file_size > 0:
	buffer = work_file.read(file_size)
	s.send(message)
	data = s.recv(buffersize)
	s.send(buffer)
	s.send(ponto_de_parada)
	#file_size -= 1024
	print file_size
	print "done"
	data = s.recv(buffersize)
	print "received data:", data
	s.close
	#print "received data:", data
	return "Post Sent!", 200 

@app.route("/api/start", methods=['GET'])
def start():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	print "Sending Start"
	s.send(start2)
	print "Start sent"
	s.close
	return "Started!", 200

@app.route("/api/stop", methods=['GET'])
def stop():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	print "Sending Stop"
	s.send(stop2)
	print "Stop sent"
	s.close
	return "Stopped!", 200

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)
