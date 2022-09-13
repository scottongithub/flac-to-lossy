import sys, os
from show_stats import show_stats
from f2l_init import f2l_init
from f2l_encode import f2l_encode

in_dir = "path/to/source_dir/" # need trailing slashes here
out_dir = "path/to/dest_dir/" # need trailing slashes here
recycle_bin = "path/to/temp_folder/" # uniished tracks from interrupted sessions get moved here (rather than deleted)
db_path = out_dir + "flac_to_lossy.db"
error_log = out_dir + "flac_to_lossy_errors.log"
target_codec = "opus" # mp3, opus, or ogg
encoder_audio_quality = "7" # For ogg, higher is better. For mp3, lower is better. Does not apply to opus
opus_bitrate = "192K" # e.g. "224K"
# locktime_threshhold (in seconds) is how to distinguish if a locked track is part of the
# current run (and must be kept) or a past, likely interrupted, run, and must be removed.
# it should be a value that you don't expect any track's encoding time to exceed
# probably no need to change it (from default 30) but here it is
locktime_threshhold_s = 30
# strings from the filepath (that indicate FLAC files) which will be replaced by flac_str_replacement
flac_strings_to_replace = ["24-192 HD FLAC", "24-176 HD FLAC", "24-192 Vinyl FLAC", "24-96 HD FLAC", "FLAC16", "16.44 FLAC", "Flac Lossless", "24Bit FLAC", "FLAC24-96", "FLAC-WEB 24-192", "16-44", "FLAC", "Flac", "flac"]

if target_codec in ["mp3", "ogg"]:
    flac_str_replacement = target_codec.upper() + "-V" + encoder_audio_quality
elif target_codec == "opus":
    flac_str_replacement = target_codec.upper() + "-" + opus_bitrate
else:
    print("\nINVALID TARGET CODEC in flac-to-lossy.py\n")
    exit()

try:
    arg_1 = str(sys.argv[1])
except:
    arg_1 = None

if arg_1 in ["-i", "--init"]:
    f2l_init( in_dir, out_dir, db_path, error_log, flac_strings_to_replace, flac_str_replacement )
elif arg_1 in ["-e", "--encode"]:
    f2l_encode( in_dir, out_dir, recycle_bin, db_path, error_log, flac_strings_to_replace, flac_str_replacement, locktime_threshhold_s, target_codec, encoder_audio_quality, opus_bitrate)
elif arg_1 in ["-s", "--status", "--show"]:
    if os.path.isfile(db_path):
        show_stats(db_path)
    else:
        print("\nno database found\n")
else:
    print("\nflac-to-lossy options:\n-i, --init: initialize file structure and database\n-e, --encode: start encoding\n-s, --status: show status\n")
