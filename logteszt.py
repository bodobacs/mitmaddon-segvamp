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

		bem = flow.request.url

		f2 = bem.split("/")[-1]
		logging.info("Short filename: "+f2)

		if "master.json" in bem:
			logging.info("Found json")
			
			#csak lementem a json-t mert tul sok mindent kell kalkulálni a filenevekkel
#			self.writefile("master.json", flow.response.content)
			
		elif "mp4" or "m4s" in bem:
			if "range=" in flow.request.url: #ezeknek egyedi a neve
				logging.info("Id in filename.")

			elif "segment-" in bem: #ezeknek a nevébe bele kell tenni a darabot azonosito kodot
				f3 = bem.split("video/")[-1].split("/chop")[0]
				logging.info("need to insert Id: "+f3)


addons = [Savemp4()]

