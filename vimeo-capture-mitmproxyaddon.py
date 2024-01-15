#vimeo-capture-mitmproxyaddon.py
#clone master.json, mp4, m4s files with directory structure from vimeo stream to concatenate with ffmpeg later
import logging
import json
import os

class Savemp4:
	clip_id = None;
	counter = 0;

	def __init__(self):
#		os.chdir(os.path.expanduser("~/temp"))
		pass

	def store_to_filename_from_url(self, content, url, cutparameters = False):
		if self.clip_id:
			splitbyclip_id = url.split(str("/" + self.clip_id + "/"))
			if len(splitbyclip_id) == 2:
				filenamepart2 = splitbyclip_id[1]
				if cutparameters:
					filenamepart2 = filenamepart2.split("?")[0]

				fullfilename = "./" + self.clip_id + "/" + filenamepart2

#				logging.info("filename: " + fullfilename)
				self.writefile(fullfilename, content)
			else:
				logging.info("URL NOT OK: " + url) #nem a tervett az url felépítése
		
	def writefile(self, filename, content):
		dirname = os.path.dirname(filename)

		if len(dirname) > 0:
			logging.info("Creating directory: {}".format(dirname))
			os.makedirs(dirname, exist_ok=True)	#!!!!!!!!

		logging.info("File: {}".format(filename))
		if os.path.isfile(filename):
			logging.info(" exists, skipping")
		else:
			self.counter += 1;
			logging.info(" storing")# number: {}").format(self.counter)
			with open(filename, "wb") as f:	#!!!!!!!!!!
				f.write(content)

	def response(self, flow):

		#filter responses by clip_id
		if "master.json" in flow.request.url:
			logging.info("Found master.json")
			#read in, create the same local folder structure
			injson = json.loads(flow.response.content)
			
			#store clip_id
			self.clip_id = injson['clip_id']
			logging.info("Found clip_id: " + self.clip_id)
			
			#save master.json
			self.store_to_filename_from_url(flow.response.content, flow.request.url, True)
#			self.writefile("master.mpd", flow.response.content)
			
		#save files in the right place
		elif self.clip_id != None and self.clip_id in flow.request.url:
			self.store_to_filename_from_url(flow.response.content, flow.request.url, False)
				
		#local script to join files


addons = [Savemp4()]
