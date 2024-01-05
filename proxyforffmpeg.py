"""Add an HTTP header to each response."""
import logging
import json
import base64
import re

class Savemp4:
	def __init__(self):
		pass

	def writefile(self, filename, content):
		logging.info( "Filew: {}".format( filename ) )
		with open( filename, "wb" ) as f:
			f.write( content )


	def response(self, flow):

		bem = flow.request.url.replace("?","_")

		f2 = bem.split("/")[-1]
		logging.info("File: "+f2)

		if "master.json" in bem:
			logging.info("Found master.json")
			
			#csak lementem a json-t mert tul sok mindent kell kalkulálni a filenevekkel
#			self.writefile("master.json", flow.response.content)
			
		elif "mp4" or "m4s" in bem:
			if "range=" in bem: #ezeknek egyedi a neve
				logging.info("Filename OK.")
				self.writefile(f2, flow.response.content)

			elif "segment-" in bem: #ezeknek a nevébe bele kell tenni a darabot azonosito kodot
				f3 = bem.split("video/")[-1].split("/chop")[0] + "_" + f2
				logging.info("Insert Id: "+f3)
				self.writefile(f3, flow.response.content)


addons = [Savemp4()]

