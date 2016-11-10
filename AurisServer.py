#!/usr/bin/python
# -*- coding: utf-8 -*-

#Imports:
from flask import Flask, request
from subprocess import Popen
import os
import socket

#Flask HTML Configurations:
app = Flask(__name__, static_url_path='', static_folder='html')

#Server Socket Configurations:
ip = '192.168.0.105' #IP to connect Arduino through Socket.
port = 3300 #Port to send data to Arduino through Socket, Arduino must listen in this port.
buffersize = 1024 #Buffer size to receive and send messages.

#Arduino Communication Flags:
message1 = "write" #Arduino Message 1: This message throws a flag to Arduino write Auris files sent through Socket into SD Card.
message2 = "start" #Arduino Message 2: This message throws a flag to Arduino play Auris files.
message3 = "stop"  #Arduino Message 3: This message throws a flag to Arduino stop execution of Auris files.
ponto_de_parada = "*" #End of file. This message notify the end of file to Arduino stop write file into SD Card.

#Path file Configurations
path1 = os.environ('AURIS_HOME_PATH') #Get Auris Home filepath.
path2 = os.environ('AURIS_FILES') #Get Auris Files filepath


'''
# Route to Generate Midi Melodies using the Auris Controller Midi-Melody Generator Module.
# The song name must be sent through URL in your Web Browser.
# Example: http://Your_IP:Port/api/generate-midi/SONG_NAME.
# PS1: The song MUST be located in ~/MUSIC_DEAF/music_for_deaf_files/audios.
'''
@app.route("/api/generate-midi/<music>", methods=['GET'])
def generate_midi(music):
	global process #Process global variable.
	path = "/.%sauris-controller/auris_controller.out" %(path1) #Auris Controller Midi-Melody Generator Module path.
	#Create Process to execute Midi-Melody Generator Module.
	process = Popen([path, "midiMelody", music]) #System call passing "midiMelody" and music name parameters.
	return "Midi Generated!", 200 #In case of success, this message should be displayed in your Web Browser.

'''
# Route to Generate Auris Melodies Files using the Auris Controller Midi-Melody Generator Module.
# The song name must be sent through URL in your Web Browser.
# Example: http://Your_IP:Port/api/generate-auris/SONG_NAME.
# PS1: You MUST generate Midi Melody first to use this route. 
# PS2: If you dont create Midi Melody File for your song, you will be not able to generate Auris Files.
'''
@app.route("/api/generate-auris/<music>", methods=['GET'])
def generate_auris(music):
	global process #Process global variable.
	path = "/.%sauris-controller/auris_controller.out" %(path1) #Auris Controller Midi-Melody Generator Module path.	
	#Create Process to execute Midi-Melody Generator Module.
	process = Popen([path, "aurisStream", music]) #System call passing "aurisStream" and music name parameters.
	return "Auris File Generated!", 200 #In case of success, this message should be displayed in your Web Browser.

'''
# Route to send Auris Melodies files to Arduino.
# The song name must be sent through URL in your Web Browser.
# Example: http://Your_IP:Port/api/arduino-post/SONG_NAME.
# PS1: Before send Auris Melody File to Arduino, you MUST fist GENERATE Midi-Melody Files using /api/generate-midi/MUSIC_NAME ...
# and GENERATE Auris-Melody Files using /api/generate-auris/MUSIC_NAME
'''
@app.route("/api/arduino-post/<music>", methods=['GET'])
def post_arduino(music):
	path = "%sauris_melodies/%s.txt" %(path2,music) #Concatenate filepath with song name received through URL Parameter.
	work_file = open(path, "rb") #Open Auris File located in "path" string variable.
	file_size = str(os.stat(path).st_size) #Get File size.

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket.
	s.connect((ip, port)) #Connect in Arduino server.
	print "Connection Succeed"
	
	#Start Sending Files:
	print "Starting Sending Files to Arduino..."
	file_size = int(file_size) #Parse file_size from Str to Int.
	buffer = work_file.read(file_size) #Read file and put in buffer.
	s.send(message1) #Send flag to Arduino write what will be sent through socket.
	data = s.recv(buffersize) #Wait Arduino start writting into SD Card.
	s.send(buffer) #Send file to Arduino.
	s.send(ponto_de_parada) #Send end of file mark to Arduino.
	print "Done Sending Files to Arduino."

	data = s.recv(buffersize) #Wait Arduino finish writting into SD Card.
	#At this pont Arduino MUST send an response to server to notify that transference was completed.
	#If none message was received, the server will stop waiting for response.
	while (data != "recebi"):
		data = s.recv(buffersize)

	print "Message Received from Arduino: ", data #Print message received from Arduino
	s.close #Close Socket
	return "Post Sent!", 200 #This message should be displayed in your Web Browser.

'''
# Route to send Start flag message to Arduino.
# To send this message, you first MUST first send Auris Melody file to Arduino using arduino-post/MUSIC_NAME route.
# You MUST send the song name through URL in yout web browser
# Example: http://Your_IP:Port/api/start/SONG_NAME.
# If you have installed all dependencies using our script installer, the song will be played in your computer using PUREDATA.
'''
@app.route("/api/start/<music>", methods=['GET'])
def start(music):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket to send message.
	s.connect((ip, port)) #Connect in Arduino Socket Server.
	print "Sending Start to Arduino"
	s.send(message2) #Send Start Message Flag to Arduino.
	print "Start Sent"
	s.close #Close Socket.
	path = "/.%sauris-core/auris-filter/src/main" %(path1) #Auris-Filter to play audio path.	
	music_path = "%saudios/%s.wav" %(path2, music) #Song file path
	#Create Process to play music.
	process = Popen([path, "1", music_path]) #System call sending "1" and music name as arguments.
	return "Started!", 200 #In case of success, this message should be displayed in your Web Browser.

'''
# Route to send Stop flag message to Arduino.
# To send this message, you first MUST first Start Arduino execution using api/start route.
'''
@app.route("/api/stop", methods=['GET'])
def stop():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket to send message.
	s.connect((ip, port)) #Connect in Arduino Socket Server.
	print "Sending Stop to Arduino"
	s.send(message3) #Send Start Message Flag to Arduino.
	print "Stop sent"
	s.close #Close Socket.
	return "Stopped!", 200 #In case of success, this message should be displayed in your Web Browser.

#Python and Flask Configurations:
if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True) #IP and Port use to send HTML Requests.