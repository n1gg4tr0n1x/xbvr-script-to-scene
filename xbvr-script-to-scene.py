#!/usr/bin/env python3

# EDIT BELOW, IF NEEDED.  Do not include a trailing slash.
# -------

XBVR_SERVER_ADDRESS = "http://192.168.1.100:9999"

# -------
# That's all you'll really need to edit


import sys, pathlib
try:
	import requests
except ModuleNotFoundError as e:
	sys.exit("`requests` module required, but not found. You may need to pip install `requests.`")


# Build API URLs based on XBVR server address
FILE_LIST_URL    = XBVR_SERVER_ADDRESS + "/api/files/list"
FILE_MATCH_URL   = XBVR_SERVER_ADDRESS + "/api/files/match"
SCENE_SCRAPE_URL = XBVR_SERVER_ADDRESS + "/api/task/singlescrape" 
SCENE_SEARCH_URL = XBVR_SERVER_ADDRESS + "/api/scene/search"


def get_scene_id_from_filename(filename:str) -> str:
	"""
	Extract the SLR scene ID number from the funscript's filename
	Returns `str` formatted as "slr-####"
	"""

	components = pathlib.Path(filename).stem.split(".")

	# The SLR-### numeric ID is third from the last group dot-separated values in the base name
	if not components[-3].isnumeric():
		raise ValueError(f"Filename is incorrect format")
	
	return f"slr-{components[-3]}"

def match_funscript_to_scene(funscript:dict, scene:dict):
	"""Instruct XBVR to Match a funscript to a scene, given the XBVR info for both"""

	file_id = funscript["id"]
	scene_id = scene["scene_id"]

	resp = requests.post(FILE_MATCH_URL, json={"file_id":file_id, "scene_id":scene_id})
	
	if not resp.status_code == 200:
		raise Exception(resp.content.decode())

def get_scenes_for_id(scene_id:str) -> list[dict]:
	"""
	Request known scene data from the XBVR API for a given scene ID
	Returns a list of XBVR info dicts for found scenes
	"""

	resp = requests.get(SCENE_SEARCH_URL, params={"q":f"+id:\"{scene_id}\""})

	if not resp.status_code == 200:
		raise Exception(str(resp.content.decode()))
	
	if resp.json()["results"] == 0:
		return []
	
	return resp.json()["scenes"]

def scrape_slr_scene_id(scene_id:str):
	"""Instruct XBVR to scrape SLR for a given scene ID"""

	if scene_id.lower().startswith("slr-"):
		scene_id = scene_id[4:]

	resp = requests.post(SCENE_SCRAPE_URL, json={
		"site": "slr-single_scene",
		"sceneurl": "https://www.sexlikereal.com/" + scene_id,
		"additional_info" : []
	})

	if not resp.status_code == 200:
		raise Exception(str(resp.content.decode()))

def get_unmatched_files_list() -> list[dict]:
	"""
	Request a list of unmatched files from the XBVR API
	Returns a list of XBVR file info dicts
	"""

	resp = requests.post(FILE_LIST_URL, json={
		"sort":"created_time_desc",
		"state":"unmatched",
		"createdDate":[],
		"resolutions":[],
		"framerates":[],
		"bitrates":[],
		"filename":""
	})

	if not resp.status_code == 200:
		raise Exception(resp.content.decode())

	return resp.json()


if __name__ == "__main__":
	"""Script starts here"""

	# Request unmatched files list from XBVR
	print("Asking XBVR for unmatched files list...")
	try:
		unmatched_files_info = get_unmatched_files_list()
	except Exception as e:
		sys.exit(f"Error getting unmatched files from XBVR: {e}")
	
	# If no unmatched files found, we're done
	if not unmatched_files_info:
		sys.exit("Nothing to do: No unmatched files found in XBVR.")
	
	print(f"XBVR has {len(unmatched_files_info)} unmatched files.  Let's see here...")

	# Loop through each unmatched file
	for funscript_info in unmatched_files_info:

		funscript_filename = pathlib.Path(funscript_info["filename"])
		
		# Skip files that aren't `.funscript`s
		if funscript_filename.suffix.lower() != ".funscript":
			print(f"Skipping {funscript_filename}: Not a funscript", file=sys.stderr)
			continue
		
		# Try to extract SLR scene ID from the filename
		try:
			scene_id = get_scene_id_from_filename(funscript_filename.name)
		except Exception as e:
			print(f"Skipping {funscript_filename}: {e} (Probably does not follow the expected file naming convention)", file=sys.stderr)
			continue

		print(f"Found funscript {funscript_filename.name} for SLR ID {scene_id}")

		# Ask XBVR for a list fo scenes matching the funscript's slr-### scene ID
		# (This basically does an XBVR search with +id:"slr-###")
		print(f"\tSearching XBVR for known scenes with ID {scene_id}...")

		try:
			scenes = get_scenes_for_id(scene_id)
		except Exception as e:
			print(f"\tError searching XBVR for scene ID {scene_id}: {e}.  Skipping.", file=sys.stderr)
			continue

		# If no scenes were found in XBVR, try to scrape it and then re-search
		if not scenes:

			print(f"\tNo existing scenes in XBVR.  Scraping SLR for scene {scene_id}...")
			try:
				scrape_slr_scene_id(scene_id)
				scenes = get_scenes_for_id(scene_id)
			except Exception as e:
				print(f"\tXBVR error during scrape and re-search: {e}. Skipping.", file=sys.stderr)
				continue


		# Moment of truth: Do we finally have this scene or, like, what
		if not scenes:
			print(f"\tNo scenes found in XBVR or SLR for {funscript_filename} :(  Skipping.", file=sys.stderr)
			continue

		# Sanity check: Let's not do anything crazy if we matched a ton of scenes or something
		if len(scenes) > 3:
			print(f"\tSuspicious results: Matched {len(scenes)} scenes for {funscript_filename}.  Skipping.", file=sys.stderr)
			continue

		print(f"\tFound {len(scenes)} scenes:")

		# Loop through each scene found in XBVR with SLR-ID (not sure if there even CAN be more than one, but it's a loop in case)
		# and perform a match between the scene and the funscript
		for scene_info in scenes:

			print(f"\t\tMatching to scene {scene_info['id']}: {scene_info['title']}...", end=" ")

			try:
				match_funscript_to_scene(funscript=funscript_info, scene=scene_info)
			except Exception as e:
				print(str(e), file=sys.stderr)
			else:
				print("Done!")
	
	# If we made it here, nothing blew up
	print("")
	print("Script matching is complete.  Have a nice wank.  You deserve it.")
