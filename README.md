# Auris-Server Script

This is one module from Auris Chair Project develped at Universidade Federal da Paraiba - UFPB
The server script was written in Python, and to use this you need the following dependencies:
- python2.7
- flask

And for many functionalities from this server, you need an Arduino UNO Connected on your local Internet.

### Installation:

Fist, you have to have installed all dependencies from [Auris-Scripts](https://gitlab.lavid.ufpb.br/auris/auris-scripts)

Go to Auris-Server folder:
```sh
$ cd ~/<MUSIC_FOR_DEAF_FOLDER>/auris_server/
```

Open AurisServer.py archive on your favorite text editor
On Server Socket Configurations, change the ip and port to the same used by your Arduino. This is the address to connect in your Arduino.

Run python archive:
```sh
$ python AurisServer.py
```

### Usage:

There are five routes for this server.
- /api/generate-midi/<music> - Route to Generate Midi Melodies using the Auris Controller Midi-Melody Generator Module.
- /api/generate-auris/<music> - Route to Generate Auris Melodies Files using the Auris Controller Midi-Melody Generator Module.
- /api/arduino-post/<music> - Route to send Auris Melodies files to Arduino.
- /api/start/<music> - Route to send Start flag message to Arduino.
- /api/stop - Route to send Stop flag message to Arduino.

### Configure Arduino:
Turn on your arduino and connect it to your local network.
Get your Arduino IP Address and Socket port.
Go to AurisServer.py file and open on your favorite text editor.
In line 14 and 15 you can change the Arduino IP Address and Socket Port.

### Generating Midi Melodies:

Go to Auris Files folder:
```sh
$ cd ~/<MUSIC_FOR_DEAF_FILES_FOLDER>/audios/
```

In this folder you can drop some Music files you want to Generate Auris Files.
For example, put the song named `song1.wav`.
The song must be in `.wav` format.

To generate Midi, open your browser and type:
```sh
$ http://127.0.0.1:5000/api/generate-midi/<Song_Name>
$ http://127.0.0.1:5000/api/generate-midi/song1
```
A `.midi` file will appear on Midi folder.

### Generating Auris File:

To generate Auris File, type on your browser:
```sh
$ http://127.0.0.1:5000/api/generate-auris/<Song_Name>
$ http://127.0.0.1:5000/api/generate-auris/song1
```
A `.txt` file will appear on auris_melodies folder.

### Sending Auris File to Arduino:

To Send file to your Arduino, type on your browser:
```sh
$ http://127.0.0.1:5000/api/arduino-post/<Song_Name>
$ http://127.0.0.1:5000/api/arduino-post/song1
```
On your server console, you will see if the song were successfully sent to Arduino.
If you obtained success, your Arduino will be waiting for Start or stop flag to start playing the auris file. Then, type on your browser:
```sh
$ http://127.0.0.1:5000/api/start/<Song_Name>
$ http://127.0.0.1:5000/api/start/song1
```
To stop the execution of Auris file, just type in on your browser:
```sh
$ http://127.0.0.1:5000/api/stop
$ http://127.0.0.1:5000/api/stop
```