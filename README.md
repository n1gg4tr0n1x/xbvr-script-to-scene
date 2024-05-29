# xbvr-script-to-scene
Match SLR funscripts (with a particular file naming convention) to their SLR scenes in XBVR.  This script does the following:

- Gets a list of unmatched scripts on an XBVR server
- Extracts the SLR scene ID from the funscript filename
- Checks XBVR for an existing scene, or instructs XBVR to scrape the scene from SLR if it hasn't been already
- Matches the script to the resulting scene

## Funscript File Naming Convention - Important!
This script only works for a particular script file naming convention, which contains the SLR ID at a particular spot near the end of the file name.  Examples of filenames that will work with this:

- `MAKE YOU MINE.scriptai-automated-scripts.43291.18949.1.funscript` - Matches to SLR-42391
- `Up Close VR with Scarlett Alexis.scriptai-automated-scripts.42630.18875.1.funscript` - Matches to SLR-42630
- `Way Too Tight For You.realcumber.43297.18790.1.funscript` - Matches to SLR-42397

Funscripts without this file naming convention will not correctly match to scenes.  In most cases, they will be skipped over.

## Requirements & Dependencies
- python3: This is a python3 script which requires a recent version of python3 to be installed on your system.
- `requests`: This script requires the `[requests](https://pypi.org/project/requests/)` library, which is a third-party library and must be manually installed before running the script
- XBVR: Access to a running instance of XBVR is required

## Configuration
Before running the script, edit the `XBVR_SERVER_ADDRESS` variable on [Line 6](https://github.com/n1gg4tr0n1x/xbvr-script-to-scene/blob/0a1fe5d1402563bb233774010d4b97e3401523a6/xbvr-script-to-scene.py#L6) to point to the server and port that XBVR is running on.  If you are running the script on the same system as XBVR, the default `localhost:9999` should work unless you know otherwise.

## Running
This is a command-line application which will communicate with XBVR.  After starting XBVR, installing the [requirements & dependencies](#requirements--dependencies), and [configuring the script](#configuration), open a terminal window to the location where the script resides, and run the following command:

### Windows
```
python xbvr-script-to-scene.py
```

### Mac & Linux
```
python3 xbvr-script-to-scene.py
```
