# Overview
## Purpose
Creates a new repository with lossy-encoded files, from a source repository with flac-encoded files, copying over all (non-flac) files and folder structures

Target codes supported: opus, ogg, and mp3

Multiple threads/encoding sessions running at the same time is supported

Encoding can be stopped (via ctrl-c) and restarted later, for larger sets. Unfinished files from the interrupted session(s) will be cleaned up and started again


## How it works
### Initialize
* creates a sqlite3 database of all files to be encoded, so state can be tracked during and in-between encode sessions
* creates a new directory structure, based on the old, that:
  + replaces flac-ey (e.g. "24-192 HD FLAC") strings in directory names with "OPUS-224K" (or whatever the encode setting is)
  + copies over all non-flac files (e.g. artwork) to their associated new directory, maintaining structure

### Encode
* removes any incomplete files left over from last (interrupted) encode session. Locktimes are used to distinguish between locked tracks that are running in the current run (and must be kept) or a past, likely interrupted, run (and must be removed)
* encodes with `ffmpeg` and places the new file into the new repository

# Prerequisites
- ffmpeg - 4.2.4 has been tested
- Python package `tinytag` is needed - 1.6 through 1.81 have been tested
- Runs on Linux

# Usage
* `git clone https://github.com/scottongithub/flac-to-lossy.git`
* `pip install tinytag`
* all configuration is at top of `flac-to-lossy.py` in/out/recycle_bin directories, codec parameters etc.
* initialize new repository and database: `python3 flac-to-lossy.py --init`
* start encoding: `python3 flac-to-lossy.py --encode`. Multiple terminal sessions are supported - it should distribute evenly among processors.
* you can interrupt encoding at any time with ctrl-c
* pick encoding back up with `python3 flac-to-lossy.py --encode` - it will remove unfinished files from last session and restart them
* for larger sets you can leave the stats (time reamining, etc.) showing as `watch flac-to-lossy.py --stats`
