import re

bemenet = "https://21vod-adaptive.akamaized.net/exp=1704286362~acl=%2Fa0aef51d-b208-432d-9da1-979889275d7c%2F%2A~hmac=5fb08846a69c3c3695ace9d93784b254375797d6e0f536edfd55d8b60a217212/a0aef51d-b208-432d-9da1-979889275d7c/sep/video/c96eb461/chop/segment-22.m4s?r=dXM%3D"

f2 = bemenet.split("/")[-1]
print("split: "+f2) #<---- ez a nyerő

	
#found = re.search("/[^/]+$",bemenet)
found = re.search("/[^/]+(mp4|m4s)[^/]+$",bemenet)

if found:
	filenev = found.group()[1:]
	print("regex: "+filenev)

f3 = bemenet.split("video/")[-1].split("/chop")[0]
print(f3)

