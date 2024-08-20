#!/usr/bin/env python
#git repo 2024.08.20
#vimeo-combine-segments.py

#import re
import json
#from pprint import pprint
import os
import sys
import base64
import subprocess

json_data = dict()
base_url = str()
#segments collected in json make a full part
track_mediafiles = list()

complete_track_ids = list()

outfilename = str()

def findfile(filename):
	if os.path.isfile(filename):
		print("Found: {}".format(filename))
#	print("Not found: {}".format(filename))

def print_video_info(track):
	print("\ntrack id: {}\n {}: {}x{}".format(track['id'], track["base_url"], track["width"], track["height"]))

def print_audio_info(track):
	print("\ntrack id: {}\n {}: {}".format(track['id'], track["base_url"], track["format"]))

def find_complete_streams(jd, branch, printme):
	# Iterate through all the tracks under the branch
	for track in jd[branch]:
		base_url_of_track = track["base_url"]
#		print(base_url_of_track)
		printme(track) #printme is a separate print function to audio and video

		segments_count = len(track["segments"]) #number of the segments in one stream
#		print("Number of segments: ", segments_count)

		#check how many files we have of those segments
		found_count = 0
		n = 0

		#registering the missing segments so I can have some clue where are the missing track_mediafiles
		first_missing = -1
		last_missing = 0

		#check all segments in the track
		for seg in track["segments"]:
			seg_url = seg["url"]

			#"range" from http-request header given to the end of the small files name
			seg_range = ''
			if "range" in seg: seg_range = "bytes=" + seg["range"]

			#create filename from data
			fn = base_url + base_url_of_track + seg_url + seg_range

			#check if the file exists and count them
			if os.path.isfile(fn):
				#print("Found: {}".format(fn))
				found_count += 1
			elif first_missing != -1:
				last_missing = n
			else:
				first_missing = n
			n += 1

		if found_count == segments_count:
			#all files exist for creating the track
			print(str("Found all {}/{} segments").format(found_count, segments_count))

			#saving the 
			global complete_track_ids
			complete_track_ids.append(track['id'])
		else: print(str("{}/{} segs found. √[{}. - {}.]").format(found_count, segments_count, first_missing, last_missing))

def create_track_media(jd):
	for branch in ["video", "audio"]:
		for track in jd[branch]:
			if track['id'] in complete_track_ids:
				newfn = branch + track["id"] + ".mp4"
				print(str("\ntrack id: {}, Creating: {}").format(track['id'], newfn))

				with open(newfn, "wb") as f_to:	#!!!!!!!!!!
					#write init seqment to file
					init_b64 = track["init_segment"]
					init_seg = base64.b64decode(init_b64)

					f_to.write(init_seg)

					write_counter = 0
					for segread in track["segments"]:
						seg_url = segread["url"]
						#"range" from http-request header given to the end of the small files name
						seg_range = ''
						if "range" in segread: seg_range = "bytes=" + segread["range"]

						#create filename from data
						fn = base_url + track['base_url'] + seg_url + seg_range

						if os.path.isfile(fn):
							with open(fn, "rb") as f_from:
								seg_data = f_from.read();
								f_to.write(seg_data)
								write_counter+=1

#					print("write counter: ", write_counter)
					if write_counter == len(track['segments']):
						global track_mediafiles
						track_mediafiles.append(newfn)
						print("All segments are written to file")

def startcheck():
	try:
		if(len(sys.argv) > 1): f = open(sys.argv[1])
		else:
			print("No input json file")
			return False

		try:
			global json_data
			json_data = json.load(f);
		except:
			print("Cannot load ")
			return False
		finally:
			f.close();
	except:
		print("Cannot open master.json" + sys.argv[1])
		return False

	if 'title' in json_data and 'outdir' in json_data and 'base_url' in json_data:
		print("title: " + json_data["title"])
		print("outdir: " + json_data["outdir"])
		print("base_url: " + json_data["base_url"])
		return True
	else:
		print('No key "title" and/or "outdir" in json')
	return False

def find_and_join():
	global base_url
	base_url = json_data["base_url"]
	if len(base_url):

		print("\n****************************video****************************")
		find_complete_streams(json_data, "video", print_video_info)

		print("\n****************************audio****************************")
		find_complete_streams(json_data, "audio", print_audio_info)

		print("\n****************************result***************************")
		create_track_media(json_data)

		if len(track_mediafiles) == 2:
			#command = "ffmpeg" -i" + track_mediafiles[0] + " -i " + track_mediafiles[1] + " out.mkv"

	#			outfilename = sys.argv[1] + ".mkv" if 2 == len(sys.argv) else "out.mkv"
	#			outfilename = os.path.expanduser('~') + "/temp/" + json_data['title'] + '.mkv'
			global outfilename
			outfilename = json_data['outdir'] + json_data['title'] + '.mkv'

			print("Calling ffmpeg to create: " + outfilename + "\n")
#mkv version was working
			result = subprocess.run(["ffmpeg", "-n", "-hide_banner", "-loglevel", "warning", "-i", track_mediafiles[0], "-i", track_mediafiles[1], "-c", "copy", outfilename])
			#'-n': no overwrite
#mp4 version needs changes because mp4 does not accept simple concatenation
#			result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-i", track_mediafiles[0], "-i", track_mediafiles[1], "-c", "copy", outfilename])
	#			subprocess.run(["ffmpeg", "-i", track_mediafiles[0], "-i", track_mediafiles[1], "-c", "copy", "out.mkv"])
			print("ffmpeg fail") if result.returncode else print("ffmpeg done")
			return True
		elif len(track_mediafiles) < 2:
			print("Missing tracks")
		elif len(track_mediafiles) > 2:
			print("Too many complete video or audio tracks, cannot decide what to include: ", track_mediafiles)
	else:
		print("Error: base_url not found")
	return False

#START
print("\nScript vimeo-combine-segments.py")
#print("Working dir: " + os.getcwd())

if startcheck() and find_and_join():
#	outfilename
	print("vimeo-combine-segments.py success, created: " + outfilename)
	sys.exit(0)

print("vimeo-combine-segments error")
sys.exit(1)
