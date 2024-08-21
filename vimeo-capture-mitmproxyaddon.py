#vimeo-capture-mitmproxyaddon.py
#git repo 2024.08.20
#clone master.json, mp4, m4s files with directory structure from vimeo stream to concatenate with ffmpeg later

import logging
import json
import os
import sys
import subprocess

class ripvimeo:
	clip_id = None
	counter = 0
	title = "title-not-found" #extracted from response example: https://player.vimeo.com/video/797295134?h=ded2a4333
	masterdir = '' #dir of master.json
	masterjson_filename = '' #now it can be master.json or playlist.json
	#workdir = os.path.expanduser('~') + "/temp/"
	workdir = "/tmp/" #place where all capture goes
	outputdir = os.path.expanduser('~') + "/temp/"
	skippingthewholevideo = False

	def __init__(self):
#		os.chdir(os.path.expanduser("~/temp"))
		os.chdir(self.workdir) #go to the baseof operation
		pass

	def get_title_and_modify_player_settings(self, response):
		#logging.info("Player starts or stops: ")

		try:
			str_content = response.content.decode("utf-8")
			if 'Vége a videónak' in str_content: #player is stopping
				#end of streaming, time to concatenate pieces
				logging.info('"Vége a videónak" found, combining segments:')

				if self.skippingthewholevideo: return

				#pop into the master.json's dir
				os.chdir(self.masterdir) #hibát ad amikor nem megy mentés mert már megvan a kimeneti fájl
				subprocess.call(["vimeo-combine-segments.py", self.masterjson_filename])
#				result = subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
				os.chdir(self.workdir)

#				if result.returncode:
#					print("FAIL: vimeo-combine-segments.py")
#				else:
#					print("Video done, no cleaning up")
#					subprocess.run(["rm", "-rf", "./" + self.clip_id + "/"])

			else: #player is starting, overwrite settings
				##1## Check if this response is a proper player settings file
				##2## Check if there is a title
				##3## Overwrite settings if possible

				#extract title
				#self.title = str_content.split("<title>")[1].split(" on Vimeo</title>")[0]
				split_title = str_content.split("<title>", 1) #do one split at the first "<title>"
				if 2 == len(split_title):
					split_at_endtag = split_title[1].split(" on Vimeo</title>", 1)
					if 2 == len(split_at_endtag):
						self.title = split_at_endtag[0]

						##checking outfile
						outfilename = self.outputdir + self.title + '.mp4'
						if os.path.isfile(outfilename):
							self.skippingthewholevideo = True
							logging.info('Outfile "{}" already exsists, skipping the whole video'.format(outfilename))
						else:
							logging.info("Title found, playing")
							logging.info("Outfile: " + outfilename)
							self.skippingthewholevideo = False

						#reset settings, autoplay, choose resolution here
						response.content = response.content.replace(b',"quality":null,', b',"quality":"240p",').replace(b'"autoplay":0,', b'"autoplay":1,')
						response.content = response.content.replace(b',"quality":null,', b',"quality":"540p",').replace(b'"autoplay":0,', b'"autoplay":1,')

						#all good
						return

					logging.info('Not found " on Vimeo</title>"')
				logging.info('Not found "<title>"')

#				#extract json for title
#				first_part = str_content.split("<script>window.playerConfig = ")
#				if 1 < len(first_part): #player is sarting
#
#					json_raw = first_part[1].split("</script>")[0]
#					json_data = json.loads(json_raw)
#					self.title = json_data['video']['title']
#					logging.info("Title: " + self.title)
#					logging.info("quality: {}".format(json_data['embed']['quality']))

		except ValueError as e:
			logging.info("Failed to read player settings")
			#itt kene visszanyomni a valtoztatasokat

	def make_filename_from_url(self, url, cutparameters = False, extra = ''):
		if self.clip_id:
			splitbyclip_id = url.split(str("/" + self.clip_id + "/"))
			if len(splitbyclip_id) == 2:
				filenamepart2 = splitbyclip_id[1]
				if cutparameters:
					filenamepart2 = filenamepart2.split("?")[0]
				return "./" + self.clip_id + "/" + filenamepart2 + extra

			else:
				logging.info("URL NOT OK: " + url)

	def writefile(self, filename, content):
		dirname = os.path.dirname(filename)

		if len(dirname) > 0:
#			logging.info("Creating directory: {}".format(dirname))
			os.makedirs(dirname, exist_ok=True)	#!!!!!!!!

		if os.path.isfile(filename):
			res = "skipping"
		else:
			self.counter += 1;
			res = "storing"
			with open(filename, "wb") as f:	#!!!!!!!!!!
				f.write(content)
			logging.info("{}: {}".format(res, filename)) #no skipping message
#		logging.info("{}: {}".format(res, filename))

	def response(self, flow):

		#catching and modifying settings transfer
		if flow.request.url.startswith("https://player.vimeo.com/video/"):
			#initialization settings arrived
			self.get_title_and_modify_player_settings(flow.response)

		#already saved content, output filename fom title exists in target dir
		if self.skippingthewholevideo: return

		#filter responses by clip_id
		if "master.json" in flow.request.url or "playlist.json" in flow.request.url:
			if "master.json" in flow.request.url: self.masterjson_filename = "master.json"
			if "playlist.json" in flow.request.url: self.masterjson_filename = "playlist.json"
			if len(self.masterjson_filename):
				logging.info("Found: " + self.masterjson_filename)
				try:
					#read in, create the same local folder structure
					injson = json.loads(flow.response.content)

					#store clip_id
					self.clip_id = injson['clip_id']
					logging.info("Found clip_id: " + self.clip_id)

					fullfilename = self.make_filename_from_url(flow.request.url, True, '')
					logging.info("filename: " + fullfilename)
					self.masterdir = os.path.dirname(fullfilename)
					logging.info("masterdir: " + self.masterdir) #save location of master.json

					#saving vimeo-combine-segments.py parameters
					injson['outdir'] = self.outputdir
					injson['title'] = self.title

					dirname = os.path.dirname(fullfilename)
					os.makedirs(dirname, exist_ok=True)
					with open(fullfilename, 'w', encoding='utf-8') as f:
						json.dump(injson, f, ensure_ascii=False, indent=4)
				except json.decoder.JSONDecodeError as e:
					print(e)

		#save files in the right place
		elif self.clip_id != None and self.clip_id in flow.request.url:
			#save file to a server-like file structure

			#they hid the range parameter in the http-request header so the filename will not change and cannot save it individually
			if 'range' in flow.request.headers:
				flow.request.headers['range']
				#extending filename with the value of "range" from http-request header
				self.writefile(self.make_filename_from_url(flow.request.url, False, flow.request.headers['range']), flow.response.content)
			else: 
				#the general
				self.writefile(self.make_filename_from_url(flow.request.url, False, ''), flow.response.content)

		#local script to join files

#	def server_connected(self, conn):
#		if "akamaized" in conn.server.address[0]:
#			logging.info("CONNECTION START akamaized")

#	def server_disconnected(self, conn):
#		if "akamaized" in conn.server.address[0]:
#			logging.info("STARTING SCRIPT")
#			logging.info("masterdir: " + self.masterdir)
#			tempdir = os.getcwd()
#			subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
#			os.chdir(tempdir)


addons = [ripvimeo()]
