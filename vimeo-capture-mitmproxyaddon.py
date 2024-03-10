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
	masterdir = '' #dir of master.json
	#workdir = os.path.expanduser('~') + "/temp/"
	workdir = "/tmp/" #place where all capture goes
	outputdir = os.path.expanduser('~') + "/temp/"

	def __init__(self):
#		os.chdir(os.path.expanduser("~/temp"))
		os.chdir(self.workdir) #go to the baseof operation
		pass

	def get_title_and_modify_player_settings(self, response):
		#logging.info("Player starts or stops: ")

		try:
			str_content = response.content.decode("utf-8")
			if 'Vége' in str_content: #player is stopping
				#end of streaming, time to concatenate pieces
				logging.info('"Vége"')

				if self.skippingthewholevideo: return

				#pop into the master.json's dir
				os.chdir(self.masterdir)
				subprocess.call(["vimeo-combine-segments.py"])
#				result = subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
				os.chdir(self.workdir)

#				if result.returncode:
#					print("FAIL: vimeo-combine-segments.py")
#				else:
#					print("Video done, no cleaning up")
#					subprocess.run(["rm", "-rf", "./" + self.clip_id + "/"])

			else: #player is starting and getting settings

				#extract title
				#self.title = str_content.split("<title>")[1].split(" on Vimeo</title>")[0]
				split_title = str_content.split("<title>", 1) #do one split at the first "<title>"
				if 2 == len(split_title):
					split_at_endtag = split_title[1].split(" on Vimeo</title>", 1)
					if 2 == len(split_at_endtag):
						self.title = split_at_endtag[0]
						logging.info("Title found, play starts")

						#reset settings
						response.content = response.content.replace(b',"quality":null,', b',"quality":"240p",').replace(b'"autoplay":0,', b'"autoplay":1,')

					else:
						logging.info("Not found title endtag: ", split_at_endtag)
						return

					##checking outfile
					outfilename = self.outputdir + self.title + '.mkv'
					if os.path.isfile(outfilename):
						self.skippingthewholevideo = True
						logging.info('Outfile "{}" already exsists, skipping the whole video'.format(outfilename))
					else:
						logging.info("Outfile: " + outfilename)
						self.skippingthewholevideo = False

				else:
					logging.info("Not the usual player content")
					return

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

	skippingthewholevideo = False
	def response(self, flow):

		if flow.request.url.startswith("https://player.vimeo.com/video/"):
			self.get_title_and_modify_player_settings(flow.response)
			#logging.info("player control request: " + flow.request.url)


		if self.skippingthewholevideo: return

		#filter responses by clip_id
		if "master.json" in flow.request.url:
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
#			subprocess.run(["vimeo-combine-segments.py"]) #concatenate with external script
#			os.chdir(tempdir)


addons = [ripvimeo()]
