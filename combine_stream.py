#combine_stream.py

import re
import json
from pprint import pprint
import os
import base64

def findfile(filename):
	if os.path.isfile(filename):
		print("Found: {}".format(filename))
#	print("Not found: {}".format(filename))

def list_segments(jd, branch):
	# Iterate through the JSON array
	for item in jd[branch]:
		pack_base_url = item["base_url"]
		print("base_url: ", pack_base_url)
		seg_count = len(item["segments"])
		print("Number of segments: ", seg_count)
		found_count = 0

		for seg in item["segments"]:
			seg_url = seg["url"]
			fn = base_url + pack_base_url + seg_url
			if os.path.isfile(fn):
				print("Found: {}".format(fn))
				found_count += 1
		if found_count == seg_count:
			print("JOIN THIS")
			
			newfn = item["id"] + ".mp4"

			print(newfn)
			with open(newfn, "wb") as f_to:	#!!!!!!!!!!
				init_b64 = item["init_segment"]
				init_seg = base64.b64decode(init_b64)
				
				f_to.write(init_seg)

				for segread in item["segments"]:
					seg_url = segread["url"]
					fn = base_url + pack_base_url + seg_url
					if os.path.isfile(fn):
						with open(fn, "rb") as f_from: #!!!!!!!!!!!
							seg_data = f_from.read();
							f_to.write(seg_data)

f = open("master.json")
json_data = json.load(f);
f.close();

base_url = json_data["base_url"]
if not len(base_url):
	exit

print("video****************************")
list_segments(json_data, "video")
print("audio****************************")
list_segments(json_data, "audio")
