#!/usr/bin/python

import re
import json
import os
import logging
from pprint import pprint
import subprocess

print("-A-")###########################################################

bemenet = "https://21vod-adaptive.akamaized.net/exp=1704286362~acl=%2Fa0aef51d-b208-432d-9da1-979889275d7c%2F%2A~hmac=5fb08846a69c3c3695ace9d93784b254375797d6e0f536edfd55d8b60a217212/a0aef51d-b208-432d-9da1-979889275d7c/sep/video/c96eb461/chop/segment-22.m4s?r=dXM%3D"

print("url: "+bemenet)

print("-B-")###########################################################

f2 = bemenet.split("/")[-1]
print("split-tel szétszedve az utolsó darab: "+f2) #<---- ez a nyerő

	
#found = re.search("/[^/]+$",bemenet)

found = re.search("/[^/]+(mp4|m4s)[^/]+$",bemenet)
if found:
	filenev = found.group()[1:]
	print("regex (az utolsó perjel nélküli perjellel elválasztott szakasz a végéig): " + filenev)

print("-C-")###########################################################

f3 = bemenet.split("video/")[-1].split("/chop")[0]
print("video/-val elválasztott darabok közül az utolsó/második, újra feldarabolva a /chop-pot megelőző darab adja vissza a id-t: " + f3)


print("-D-")###########################################################

print("split-tel elválasztva a clip_id előtt és utáni szakasz:")
clip_id = "a0aef51d-b208-432d-9da1-979889275d7c"

splitbyclip_id = bemenet.split("/" + clip_id + "/")
print("0: " + splitbyclip_id[0])
print("1: " + splitbyclip_id[1])
print("num of splits: ", len(splitbyclip_id))


print("-E-")###########################################################

filename = "./master.json"
print("Reading: ", filename,)
print( "File: {}".format( filename ) )
with open( filename, "r" ) as f:
	content = f.read()

loadedjson = json.loads(content)
print(type(loadedjson))

#pprint(loadedjson)

pprint(loadedjson['clip_id'])

print("-F-")###########################################################
print(os.getcwd())
print(os.path.expanduser("~/temp"))
os.chdir(os.path.expanduser("~/temp"))
print(os.getcwd())

print("-G-")###########################################################

#os.system('play -nq -t alsa synth {} sine {}'.format(1, 440))
#os.system('aplay /usr/share/sounds/purple/alert.wav')
print('\007')
print("\a")

print("-F-")###########################################################

szoveg = "<title>bla bla1 bla2 bla3 bla4</title>"
split = szoveg.split("bla1")
print("split: ", split)

print("-G-")###########################################################

subprocess.call(["runme.py"])
