#!/usr/bin/env python
#vimeo-combine-segments.py

import re
import json
from pprint import pprint
import os
import base64
import subprocess

#segments collected in json make a full part
parts = list()

def findfile(filename):
	if os.path.isfile(filename):
		print("Found: {}".format(filename))
#	print("Not found: {}".format(filename))

def print_video_info(item):
	print("\n{}: {}x{}".format(item["base_url"], item["width"], item["height"]))

def print_audio_info(item):
	print("\n{}: {}".format(item["base_url"], item["format"]))

def list_segments(jd, branch, printme):
	# Iterate through the JSON array
	for item in jd[branch]:
		pack_base_url = item["base_url"]
#		print(pack_base_url)
		printme(item)
		seg_count = len(item["segments"])
#		print("Number of segments: ", seg_count)
		found_count = 0
		n = 0

		first_missing = -1
		last_missing = 0

		#check all segments in track
		for seg in item["segments"]:
			seg_url = seg["url"]
			fn = base_url + pack_base_url + seg_url
			if os.path.isfile(fn):
#				print("Found: {}".format(fn))
				found_count += 1
			elif first_missing != -1:
				last_missing = n
			else:
				first_missing = n
			n += 1

		if found_count == seg_count:
			#a megtalált szegmensek száma megegyezik a jsonban lévők számával
			newfn = branch + item["id"] + ".mp4"
			print(str("Found all {}/{} segs. Creating: {}").format(found_count, seg_count, newfn))

			global parts
			parts.append(newfn)

#			print("New file: " + newfn)
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
		else:
			print(str("{}/{} segs found. √[{}. - {}.]").format(found_count, seg_count, first_missing, last_missing))

f = open("master.json")
json_data = json.load(f);
f.close();

base_url = json_data["base_url"]
if len(base_url):
	print("\n****************************video****************************")
	list_segments(json_data, "video", print_video_info)
	print("\n****************************audio****************************")
	list_segments(json_data, "audio", print_audio_info)

	print("\n****************************result***************************")
	if len(parts) == 2:
		#command = "ffmpeg" -i" + parts[0] + " -i " + parts[1] + " out.mkv"
		print("Calling ffmpeg: \n")
		subprocess.run(["ffmpeg", "-i", parts[0], "-i", parts[1], "-c", "copy", "out.mkv"])
		subprocess.run(["rm", "*.mp4"])
	else:
		if len(parts) == 0:
			print("No tracks were made")
		elif len(parts) > 2:
			print("Too many complete video or audio tracks, cannot decide what to include: ", parts)
else:
	print("Error: base_url not found")
