import os, sqlite3, subprocess, shutil
from time import time, sleep
from tinytag import TinyTag
from show_stats import show_stats

def f2l_encode( in_dir, out_dir, recycle_bin, db_path, error_log, flac_strings_to_replace, flac_str_replacement, locktime_threshhold_s, target_codec, encoder_audio_quality, opus_bitrate ):

    if not os.path.isfile(db_path):
        print("\nDATABASE NOT INITIALIZED YET\n")
        exit()

    #display progress as of last run + scrolling device for fun
    show_stats(db_path)
    for i in range(1, 80, 2):
        sleep(1 / i)
        print()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Clean up all unfinished files from the last (interrupted) run
    query = 'SELECT id, dir_suffix, filename, locktime_s FROM tracks WHERE locked = 1 and finished = 0'
    rows = c.execute(query)
    rows = rows.fetchall()
    for row in rows:
        curr_time = int(time())
        lock_time = row[3]
        # See flac-to-lossy.py for the thinking regarding threshold
        if curr_time - lock_time > locktime_threshhold_s:
            id = row[0]
            dir_suffix_orig = row[1]
            dir_suffix_lossy = dir_suffix_orig
            for string_to_replace in flac_strings_to_replace:
                dir_suffix_lossy = dir_suffix_lossy.replace(string_to_replace, flac_str_replacement)
            filename = row[2]
            filename_base = os.path.splitext(filename)[0]
            source_dir = in_dir + dir_suffix_orig
            source_full_path = source_dir + "/" + filename
            tag = TinyTag.get(source_full_path)
            title = tag.title
            artist = tag.artist
            album = tag.album
            track = tag.track
            disc = tag.disc
            dest_dir = out_dir + dir_suffix_lossy
            # title_sanitized = ""
            # for character in title:
            #     if character.isalnum() or character in [" ", "-", "+", "&", "(", ")", "[", "]", "'"]:
            #         title_sanitized += character
            # outfile = dest_dir + "/" + track + " - " + title_sanitized + "." + target_codec
            outfile = dest_dir + "/" + filename_base + "." + target_codec
            shutil.move(outfile, recycle_bin)
            query = 'UPDATE tracks SET locked = 0, finished = 0 WHERE id = ?'
            c.execute(query, (id, ))
            conn.commit()


    while True:
        query = 'SELECT id, dir_suffix, filename FROM tracks WHERE locked = 0 and finished = 0 LIMIT 1'
        rows = c.execute(query)
        row = rows.fetchone()
        if row == None:
            print("\n\nDONE\n\n")
            exit()
        id = row[0]
        dir_suffix_orig = row[1]
        filename = row[2]
        filename_base = os.path.splitext(filename)[0]
        dir_suffix_lossy = dir_suffix_orig
        for string_to_replace in flac_strings_to_replace:
            dir_suffix_lossy = dir_suffix_lossy.replace(string_to_replace, flac_str_replacement)
        source_dir = in_dir + dir_suffix_orig
        source_full_path = source_dir + "/" + filename
        timestamp = int(time())
        query = 'UPDATE tracks SET locked = 1, locktime_s = ? where id = ?'
        c.execute(query, (timestamp,id,))
        conn.commit()
        tag = TinyTag.get(source_full_path)
        title = tag.title
        artist = tag.artist
        album = tag.album
        track = tag.track
        disc = tag.disc
        dest_dir = out_dir + dir_suffix_lossy

        # title_sanitized = ""
        # for character in title:
        #     if character.isalnum() or character in [" ", "-", "+", "&", "(", ")", "[", "]", "'"]:
        #         title_sanitized += character
        outfile = dest_dir + "/" + filename_base + "." + target_codec
        encoded_by_tag = "encoded_by=ffmpeg -q:a " + encoder_audio_quality
        if target_codec in ["mp3", "ogg"]:
            ffmpeg_command = [ "ffmpeg", "-i", source_full_path, "-q:a", encoder_audio_quality, "-map_metadata", "0", "-metadata", encoded_by_tag, outfile ]
        elif target_codec == "opus":
            ffmpeg_command = [ "ffmpeg", "-i", source_full_path, "-b:a", opus_bitrate, outfile ]
        subprocess.run(ffmpeg_command)
        timestamp = int(time())
        query = 'UPDATE tracks SET locked = 0, finished = 1, donetime_s = ? WHERE id = ?'
        c.execute(query, (timestamp, id, ))
        conn.commit()

    if conn:
        conn.close()
