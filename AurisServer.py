#!/usr/bin/python
# -*- coding: utf-8 -*-

#Imports:
from flask import Flask, request, render_template, Response, jsonify, send_from_directory
from subprocess import Popen
import os
import socket
import json

#Path file Configurations
path1 = os.environ.get('AURIS_HOME_PATH') #Get Auris Home filepath.
path2 = os.environ.get('AURIS_FILES') #Get Auris Files filepath

#Flask HTML Configurations:
app = Flask(__name__, static_url_path='', static_folder='auris-front', template_folder="auris-front/templates")
app.config['UPLOAD_FOLDER_MUSIC'] = "%s/audios" %(path2) #path to save uploaded songs.
app.config['UPLOAD_FOLDER_AURIS_CFG'] = "%s/auris-core/auris-stream/file" %(path1) #path to save uploaded songs.
app.config['ALLOWED_EXTENSIONS'] = set(['wav', 'mp3', 'txt']) #Extensions supported by Auris Midi Melody Generator.

#Server Socket Configurations:
buffersize = 1024 #Buffer size to receive and send messages.

#Arduino Communication Flags:
message1 = "write" #Arduino Message 1: This message throws a flag to Arduino write Auris files sent through Socket into SD Card.
message2 = "start" #Arduino Message 2: This message throws a flag to Arduino play Auris files.
message3 = "stop"  #Arduino Message 3: This message throws a flag to Arduino stop execution of Auris files.
ponto_de_parada = "#" #End of file. This message notify the end of file to Arduino stop write file into SD Card.

@app.route('/')
def index():
    return app.send_static_file('index.html')

'''
# Route to Generate Midi Melodies using the Auris Controller Midi-Melody Generator Module.
# The song name must be sent through URL in your Web Browser.
# Example: http://Your_IP:Port/api/generate-midi/SONG_NAME.
# PS1: The song MUST be located in ~/MUSIC_DEAF/music_for_deaf_files/audios.
'''
@app.route("/api/generate-midi/<music>", methods=['GET'])
def generate_midi(music):
	global process #Process global variable.
	path = "/.%s/auris-controller/auris_controller.out" %(path1) #Auris Controller Midi-Melody Generator Module path.
	#Create Process to execute Midi-Melody Generator Module.
	process = Popen([path, "midiMelody", music]) #System call passing "midiMelody" and music name parameters.
	process.wait()
	return Response(status=200) #In case of success, this message should be displayed in your Web Browser.

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
	path = "/.%s/auris-controller/auris_controller.out" %(path1) #Auris Controller Midi-Melody Generator Module path.	
	#Create Process to execute Midi-Melody Generator Module.
	process = Popen([path, "aurisStream", music]) #System call passing "aurisStream" and music name parameters.
	process.wait()
	return Response(status=200) #In case of success, this message should be displayed in your Web Browser.

@app.route("/api/download-auris/<music>", methods=['GET'])
def download_auris(music):
	music_path = "%s/auris_melodies/" %(path2) #Song file path
	filename = "%s.txt" %(music) #Song name
	return send_from_directory(directory=music_path, filename=filename)

@app.route("/api/download-audio-filtered/<music>", methods=['GET'])
def download_audio_filtered(music):
	music_path = "%s/audios_filtered/" %(path2) #Song file path
	filename = "%s_filtered.wav" %(music) #Song name
	return send_from_directory(directory=music_path, filename=filename, as_attachment=True)

@app.route("/api/play-music/<music>", methods=['GET'])
def play_song(music):
	music_path = "%s/audios_filtered/" %(path2) #Song file path
	filename = "%s_filtered.wav" %(music) #Song name
	return send_from_directory(directory=music_path, filename=filename)

@app.route("/api/play-video/<video>", methods=['GET'])
def play_video(video):
	video_path = "%s/videos/" %(path2) #Song file path
	filename = "%s.mp4" %(video) #Song name
	return send_from_directory(directory=video_path, filename=filename)

'''
# Route to send Auris Melodies files to Arduino.
# The song name must be sent through URL in your Web Browser.
# Example: http://Your_IP:Port/api/arduino-post/SONG_NAME.
# PS1: Before send Auris Melody File to Arduino, you MUST fist GENERATE Midi-Melody Files using /api/generate-midi/MUSIC_NAME ...
# and GENERATE Auris-Melody Files using /api/generate-auris/MUSIC_NAME
'''
@app.route("/api/arduino-post/<ip>/<port>/<music>", methods=['GET'])
def post_arduino(ip, port, music):
	path = "%s/auris_melodies/%s.txt" %(path2,music) #Concatenate filepath with song name received through URL Parameter.
	work_file = open(path, "rb") #Open Auris File located in "path" string variable.
	file_size = str(os.stat(path).st_size) #Get File size.
	port = int(port)

	print "Connecting ip: ", ip
	print "At port: ", port
	print "Music: ", music

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket.
	s.connect((ip, port)) #Connect in Arduino server.
	print "Connection Succeed"
	
	#Start Sending Files:
	s.send("searc") #Send flag to Arduino write what will be sent through socket.
	s.send(music)
	s.send(ponto_de_parada)

	data = s.recv(buffersize)
	while True:
		if data == "not":
			break
		if data == "yes":
			break 

	print(data)

	if data == "not":
		#s.send(message1) #Send flag to Arduino write what will be sent through socket.
		#data = s.recv(buffersize) #Wait Arduino start writting into SD Card.
		print "Starting Sending Files to Arduino..."
		file_size = int(file_size) #Parse file_size from Str to Int.
		buffer = work_file.read(file_size) #Read file and put in buffer.
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
	return Response(status=200) #This message should be displayed in your Web Browser.

'''
# Route to send Start flag message to Arduino.
# To send this message, you first MUST first send Auris Melody file to Arduino using arduino-post/MUSIC_NAME route.
# You MUST send the song name through URL in yout web browser
# Example: http://Your_IP:Port/api/start/SONG_NAME.
# If you have installed all dependencies using our script installer, the song will be played in your computer using PUREDATA.
'''
@app.route("/api/start/<ip>/<port>", methods=['GET'])
def start(ip, port):
	port = int(port)

	print "Connecting ip: ", ip
	print "At port: ", port

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket to send message.
	s.connect((ip, port)) #Connect in Arduino Socket Server.
	print "Sending Start to Arduino"
	s.send(message2) #Send Start Message Flag to Arduino.
	print "Start Sent"
	s.close #Close Socket.
	#path = "/.%s/auris-core/auris-filter/src/main" %(path1) #Auris-Filter to play audio path.	
	#music_path = "%s/audios/%s.wav" %(path2, music) #Song file path
	#Create Process to play music.
	#process = Popen([path, "1", music_path]) #System call sending "1" and music name as arguments.
	return Response(status=200) #In case of success this message should be displayed in your Web Browser.

'''
# Route to send Stop flag message to Arduino.
# To send this message, you first MUST first Start Arduino execution using api/start route.
'''
@app.route("/api/stop/<ip>/<port>", methods=['GET'])
def stop(ip, port):
	port = int(port)

	print "Connecting ip: ", ip
	print "At port: ", port

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create Socket to send message.
	s.connect((ip, port)) #Connect in Arduino Socket Server.
	print "Sending Stop to Arduino"
	s.send(message3) #Send Start Message Flag to Arduino.
	print "Stop sent"
	s.close #Close Socket.
	return Response(status=200) #In case of success, this message should be displayed in your Web Browser.

@app.route("/api/audio-generate/<music>/<freq_corte>/<ganho>", methods=['GET'])
def audio_generate(music, freq_corte, ganho):
	#freq_corte = int(freq_corte)
	#ganho = int(ganho)

	print freq_corte
	print ganho

	path = "/.%s/auris-core/auris-filter/Auris_Essentia/Essentia_final" %(path1) #Auris-Filter to play audio path.
	music_path = "%s/audios/%s.wav" %(path2, music) #Song file path
	filtered_path = "%s/audios_filtered/%s_filtered.wav" %(path2, music) #Song file path
	process = Popen([path, "2", music_path, filtered_path, freq_corte, ganho]) #System call sending "1" and music name as arguments.
	process.wait
	return Response(status=200)

'''
# Method to verify if the uploaded file is supported by Auris Melody Generator.
'''
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

'''
# This route handles uploaded files and check if the extension is supported.
# In case of supported extension, for audios it will save the uploaded archive in AURIS_FILES/audios folder.
# For text files, it will save the uploaded archive in AURIS_FILES/auris_melodies folder.
'''
@app.route('/upload_file', methods=['POST'])
def upload():
    file = request.files['file'] # Get the name of the uploaded file
    filename = file.filename #Get filename
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Move the file from the temporal folder to the upload folder setup earlier
        # If is an audio, save in audios folder
        if filename.find(".wav") > 0 or filename.find(".mp3") > 0:
        	file.save(os.path.join(app.config['UPLOAD_FOLDER_MUSIC'], filename))
        # If is text file, save in auris_melodies folder.
        elif filename.find(".txt") > 0:
        	file.save(os.path.join(app.config['UPLOAD_FOLDER_AURIS_CFG'], "configure.txt"))
        # Redirect the user to the uploaded_file route, which will basicaly show on the browser the uploaded file
        response=Response(status=200)
        return response

#Python and Flask Configurations:
if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5501, debug=True, threaded=True) #IP and Port use to send HTML Requests.