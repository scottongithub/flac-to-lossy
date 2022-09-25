import sys, os, sqlite3, multiprocessing, subprocess
from time import time, sleep
from multiprocessing import get_context
from show_stats import show_stats
from f2l_init import f2l_init
from f2l_encode import f2l_encode, f2l_cleanup

in_dir = "/path/to/source/" # needs trailing slash
out_dir = "/path/to/dest/" # needs trailing slash
recycle_bin = "/path/to/temp/" # needs trailing slash; unfinished tracks from interrupted sessions get moved here (rather than deleted)
db_path = out_dir + "flac_to_lossy.db"
error_log = out_dir + "flac_to_lossy_errors.log"
target_codec = "opus" # mp3, opus, or ogg
opus_bitrate = "192K" # e.g. "224K"
encoder_audio_quality = "7" # 0-9; For ogg, higher is better. For mp3, lower is better. Does not apply to opus
# strings from the filepath (that indicate FLAC files) which will be replaced by flac_str_replacement
flac_strings_to_replace = ["24-192 HD FLAC", "24-176 HD FLAC", "24-192 Vinyl FLAC", "24-96 HD FLAC", "FLAC16", "16.44 FLAC", "Flac Lossless", "24Bit FLAC", "FLAC24-96", "FLAC-WEB 24-192", "16-44", "FLAC", "Flac", "flac"]
# number of encoding sessions at once, distributed across processors
processes_in_pool = multiprocessing.cpu_count() - 1
current_session_id = int(time()) # used to distinguish (locked) tracks from previous sessions that have been interrupted, from currently running (locked) tracks
# terminal highlighting
color_1 = '\33[33m'
color_default = '\x1b[0m'


if target_codec in ["mp3", "ogg"]:
    flac_str_replacement = target_codec.upper() + "-V" + encoder_audio_quality
elif target_codec == "opus":
    flac_str_replacement = target_codec.upper() + "-" + opus_bitrate
else:
    print("\nINVALID TARGET CODEC specified in flac-to-lossy.py\n")
    exit(1)

try:
    arg_1 = str(sys.argv[1])
except:
    arg_1 = None

if __name__ == '__main__':

    if arg_1 in ["-i", "--init"]:
        f2l_init( in_dir, out_dir, db_path, error_log, flac_strings_to_replace, flac_str_replacement )

    elif arg_1 in ["-e", "--encode"]:
        if not os.path.isfile(db_path):
            print("\nDATABASE NOT INITIALIZED YET\n")
            exit(1)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        query = 'SELECT integer_0 FROM misc WHERE id = "all_done"'
        all_done_query = c.execute(query)
        rows = all_done_query.fetchall()
        all_done = int(rows[0][0])
        if all_done == 1:
            print("\nALL TRACKS HAVE BEEN ENCODED\n")
            exit(0)

        query = 'UPDATE misc SET integer_0 = 0 WHERE id = ?'
        c.execute(query, ("session_row_count",))
        conn.commit()

        # remove interrupted tracks from last session and reset them in the db
        f2l_cleanup( in_dir, out_dir, recycle_bin, db_path, error_log, flac_strings_to_replace, flac_str_replacement, target_codec, encoder_audio_quality, opus_bitrate, current_session_id )

        with get_context("spawn").Pool(processes_in_pool) as p:
            for i in range(processes_in_pool):
                os.system("clear")
                p.apply_async(f2l_encode, args=(in_dir, out_dir, recycle_bin, db_path, error_log, flac_strings_to_replace, flac_str_replacement, target_codec, encoder_audio_quality, opus_bitrate, current_session_id))
                print("starting worker", i + 1, "of", processes_in_pool)
                sleep(.5)

            while all_done == 0:
                os.system('clear')
                print(color_1, "\n\nFlac-to-Lossy\n", color_default)
                print("number of workers:          ", len(multiprocessing.active_children()))
                show_stats(db_path)
                c = conn.cursor()
                query = 'SELECT integer_0 FROM misc WHERE id = "all_done"'
                all_done_query = c.execute(query)
                rows = all_done_query.fetchall()
                all_done = int(rows[0][0])
                sleep(1)

            p.close()
            p.join()

        print("\nDONE\n\n")
        if conn:
            conn.close()
        # TODO - echo is suppressed when returning to shell so this resets it
        subprocess.run(["stty", "sane"])


    elif arg_1 in ["-s", "--status", "--show"]:
        if os.path.isfile(db_path):
            show_stats(db_path)
        else:
            print("\nno database found\n")

    else:
        print("\nflac-to-lossy options:\n-i, --init: initialize file structure and database\n-e, --encode: start encoding\n-s, --status: show status\n")
