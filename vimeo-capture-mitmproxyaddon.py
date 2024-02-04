#vimeo-capture-mitmproxyaddon.py
#clone master.json, mp4, m4s files with directory structure from vimeo stream to concatenate with ffmpeg later
import logging
import json
import os
import sys
import subprocess

class ripvimeo:
	clip_id = None
	counter = 0
	title = "dummyname" #extracted from response example: https://player.vimeo.com/video/797295134?h=ded2a4333
	masterdir = str() #dir of master.json
	#workdir = os.path.expanduser('~') + "/temp/"
	workdir = "/tmp/"
	outputdir = os.path.expanduser('~') + "/temp/"

	def __init__(self):
#		os.chdir(os.path.expanduser("~/temp"))
		pass

	def get_title_and_modify_player_settings(self, response):
		#logging.info("Player starts or stops: ")

		try:
			str_content = response.content.decode("utf-8")
			if 'Vége' in str_content: #player is stopping
				#end of streaming, time to concatenate pieces
				logging.info("Play ends")

				os.chdir(self.masterdir)
				result = subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
				if result.returncode:
					print("FAIL: vimeo-combine-segments.py")
				else:
					print("Video done, cleaning up")
					os.chdir(self.workdir)
					subprocess.run(["rm", "-rf", "./" + self.clip_id + "/"])

			else: #player is starting and getting settings
				logging.info("Play starts")
				os.chdir(self.workdir)
				response.content = response.content.replace(b',"quality":null,', b',"quality":"240p",').replace(b'"autoplay":0,', b'"autoplay":1,')

				#extract title
				#self.title = str_content.split("<title>")[1].split(" on Vimeo</title>")[0]
				split_title = str_content.split("<title>")
				if split_title:
					self.title = split_title[1].split(" on Vimeo</title>")[0]
					logging.info("Title: " + self.title )
				else:
					logging.info("Not the usual player content")

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

	def make_filename_from_url(self, url, cutparameters = False):
		if self.clip_id:
			splitbyclip_id = url.split(str("/" + self.clip_id + "/"))
			if len(splitbyclip_id) == 2:
				filenamepart2 = splitbyclip_id[1]
				if cutparameters:
					filenamepart2 = filenamepart2.split("?")[0]
				return "./" + self.clip_id + "/" + filenamepart2

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
		logging.info("{}: {}".format(res, filename))

	def response(self, flow):

		if flow.request.url.startswith("https://player.vimeo.com/video/"):
			self.get_title_and_modify_player_settings(flow.response)
			logging.info("url: " + flow.request.url)

		#filter responses by clip_id
		elif "master.json" in flow.request.url:
			logging.info("Found master.json")
			#read in, create the same local folder structure
			injson = json.loads(flow.response.content)
			
			#store clip_id
			self.clip_id = injson['clip_id']
			logging.info("Found clip_id: " + self.clip_id)
			
			fullfilename = self.make_filename_from_url(flow.request.url, True)
			logging.info("filename: " + fullfilename)
			self.masterdir = os.path.dirname(fullfilename)
			logging.info("masterdir: " + self.masterdir) #save location of master.json

			#saving vimeo-combine-segments.py parameters
			injson['masterdir'] = self.masterdir
			injson['outdir'] = self.outputdir
			injson['title'] = self.title

			dirname = os.path.dirname(fullfilename)
			os.makedirs(dirname, exist_ok=True)
			with open(fullfilename, 'w', encoding='utf-8') as f:
				json.dump(injson, f, ensure_ascii=False, indent=4)

		#save files in the right place
		elif self.clip_id != None and self.clip_id in flow.request.url:
			self.writefile(self.make_filename_from_url(flow.request.url, False), flow.response.content)

		#local script to join files

#	def server_connected(self, conn):
#		if "akamaized" in conn.server.address[0]:
#			logging.info("CONNECTION START akamaized")

#	def server_disconnected(self, conn):
#		if "akamaized" in conn.server.address[0]:
#			logging.info("STARTING SCRIPT")
#			logging.info("masterdir: " + self.masterdir)
#			tempdir = os.getcwd()
#			os.chdir(self.masterdir)
#			subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
#			os.chdir(tempdir)


addons = [ripvimeo()]
