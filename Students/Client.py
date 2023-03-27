from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os, re
from typing import Optional

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.counter = 0
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler."""
	#TODO
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)

	
	def exitClient(self):
		"""Teardown button handler."""
	#TODO
		if self.state != self.INIT:
			self.sendRtspRequest(self.TEARDOWN)



	def pauseMovie(self):
		"""Pause button handler."""
	#TODO
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)		

	
	def playMovie(self):
		"""Play button handler."""
	#TODO
		if self.state == self.READY:
			self.sendRtspRequest(self.PLAY)		
	
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO

		while True:
				# close the RTP socket
			if self.teardownAcked == 1:
				# self.playEvent.set()
				self.rtpSocket.close()
				for i in os.listdir():
					if i.find(CACHE_FILE_NAME) == 0:
						os.remove(i)
				self.rtspSeq = 0
				self.sessionId = 0
				self.requestSent = -1
				self.teardownAcked = 0
				self.frameNbr = 0
				self.counter = 0
				self.label.pack_forget()
				self.label.image = ''		
				break	
			# Stop listening upon requesting PAUSE or TEARDOWN
			if self.playEvent.isSet(): 
				break
			try:
				data = self.rtpSocket.recv(20480) # -> đọc tối đa 20480 bytes
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data) # giải mã data
					
					currFrameNbr = rtpPacket.seqNum()
					print("Current Seq Num: " + str(currFrameNbr))

					try:
						print(self.frameNbr +1,'--',rtpPacket.seqNum())
						if self.frameNbr + 1 != rtpPacket.seqNum():
							self.counter += 1 #flag khi mất gói tin
							print('!' * 60 + "\nPACKET LOSS\n" + '!' * 60)
						currFrameNbr = rtpPacket.seqNum() # gán làm qq gì ?
					# version = rtpPacket.version()
					except:
						print("seqNum() Loi \n")
						traceback.print_exc(file=sys.stdout)
						print("\n")
					if currFrameNbr > self.frameNbr: # Discard the late packet
						self.frameNbr = currFrameNbr
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except:
				# Upon receiving ACK for TEARDOWN request,
				pass

					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
	#TODO
		filename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(filename, "wb")
		file.write(data)
		file.close()
		
		return filename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
	#TODO
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=288) 
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
	#TODO
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		if requestCode == self.SETUP and self.state == self.INIT: # chưa làm gì hết !
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "SETUP %s RTSP/1.0\nCSeq: %d\nTRANSPORT: RTP/UDP; client_port= %d" % (self.fileName, self.rtspSeq, self.rtpPort)

			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.SETUP
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "PLAY %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
			
			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.PLAY
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "PAUSE %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
			
			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.PAUSE
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			# ...
			self.rtspSeq = self.rtspSeq + 1
			# Write the RTSP request to be sent.
			# request = ...
			request = "TEARDOWN %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
			
			# Keep track of the sent request.
			# self.requestSent = ...
			self.requestSent = self.TEARDOWN
		else:
			return
		
		# Send the RTSP request using rtspSocket.
		# ...
		self.rtspSocket.send(request.encode())
		print('\nDu lieu gui:\n' + request)
		
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		# TODO
		while True:
			reply = self.rtspSocket.recv(1024) # 1024 bytes
			
			if reply: 
				self.parseRtspReply(reply.decode("utf-8"))

	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		#TODO
		lines = data.split('\n') # lines là list chứa các string trả về từ server
		seqNum = int(lines[1].split(' ')[1])
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
						#-------------
						# TO COMPLETE
						#-------------
						# Update RTSP state.
						# self.state = ...
						self.state = self.READY
						# Open RTP port.
						self.openRtpPort() 
					elif self.requestSent == self.PLAY:
						# self.state = ...
						self.state=self.PLAYING
						# self.checkPlay = True
						# Create a new thread to listen for RTP packets
						self.playEvent = threading.Event() # tạo ra một kênh kết nối chờ đợi 1 event giữa các thread
						threading.Thread(target=self.listenRtp).start()
						self.playEvent.clear()
					elif self.requestSent == self.PAUSE:
						# self.state = ...
						self.state=self.READY
						# The play thread exits. A new thread is created on resume.
						self.playEvent.set() # tạm dừng thread lại

					elif self.requestSent == self.TEARDOWN:
						# self.state = ...
						self.state = self.INIT
						# Flag the teardownAcked to close the socket.
						self.teardownAcked = 1
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		self.checkSocketIsOpen = True
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket.AF_INET là dùng cho IPV4, socket.SOCK_DGRAM là dùng cho UDP
		#-> tạo ra 1 đối tượng socket dùng cho IPV4 và có giao thức UDP

		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket.settimeout(0.5)
		try:
			# Bind the socket to the address using the RTP port given by the client user
			# ...
			self.state = self.READY
			self.rtpSocket.bind(('', self.rtpPort))
		except:
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort) # trong th nào ?
		

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		self.pauseMovie()
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
			self.rtspSocket.close()
			self.master.destroy()  # Close the gui window
			sys.exit(0)		
