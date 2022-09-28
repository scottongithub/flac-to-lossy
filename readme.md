# Overview
## What it does
Takes a directory containing flac-encoded files and outputs a new directory replacing all flac files with their lossy versions. All other folders/files (e.g. album art) copied over and preserved

Target codes supported: opus, ogg, and mp3

Uses multiple processes by default, configurable at the top of flac-to-lossy.py  

Encoding can be stopped (ctrl-c) and restarted later, for larger sets. Unfinished files from the interrupted session(s) will be cleaned up and started again


## How it does it
### Initialize
* creates a sqlite3 database of all files to be encoded, so state can be tracked during and between encode sessions
* creates a new directory structure, based on the old, that:
  + replaces flac-ey (e.g. "24-192 HD FLAC") strings in directory names with their lossy equivalents (e.g. "OPUS-224K")
  + copies over all non-flac files (e.g. artwork) to their associated new directory, maintaining structure

### Encode
* removes any incomplete files left over from last (interrupted) encode session. `session_id`, based on timestamp, is used to determine if locked tracks are part of a past, interrupted run.
* encodes (remaining pending) files with `ffmpeg` into the destination directory

# Prerequisites
- ffmpeg - 4.2.4 through 4.2.7 have been tested
- Python package `tinytag` is needed - 1.6 through 1.81 have been tested
- Runs on Linux

# Usage
* `pip install tinytag`
* `git clone https://github.com/scottongithub/flac-to-lossy.git`
* all configuration is at top of `flac-to-lossy.py` - in/out/recycle_bin directories, codec parameters, multiprocessing, etc.
* initialize new repository and database: `python3 flac-to-lossy.py --init`
* start encoding: `python3 flac-to-lossy.py --encode`. Progress will be shown as it runs:

<p align="left">
<img src="https://user-images.githubusercontent.com/21364725/192796755-f91bc0a4-951e-400c-8d0c-33945d30e5df.png" width="250" />
</p>

* you can interrupt encoding at any time with ctrl-c
* pick encoding back up with `python3 flac-to-lossy.py --encode` - it will remove unfinished files from last session and restart them
