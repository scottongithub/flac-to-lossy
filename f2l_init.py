import os, sqlite3, shutil
from tinytag import TinyTag
from show_stats import show_stats

def f2l_init( in_dir, out_dir, db_path, error_log, flac_strings_to_replace, flac_str_replacement ):

    if os.path.isfile(db_path):
        print("\ninitialization has already taken place\nremove contents of destination folder to re-initialize\n")
        exit()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = 'CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT, album TEXT,  \
            title TEXT, track_num TEXT, duration_s TEXT, bitrate TEXT, dir_suffix TEXT, filename TEXT, \
            locked INTEGER DEFAULT 0, locktime_s INTEGER, donetime_s INTEGER, finished INTEGER DEFAULT 0)'
    c.execute(query)
    query = 'CREATE TABLE IF NOT EXISTS misc(id TEXT PRIMARY KEY, integer_0 INTEGER)'
    c.execute(query)
    query = 'INSERT OR IGNORE INTO misc(id, integer_0) VALUES (?,?);'
    c.execute(query, ("session_row_count", 0,))
    conn.commit()

    # set up destination directory structure and copy non-flac files over
    for (root,dirs,files) in os.walk(in_dir, topdown=True):
        for filename in files:
            dir_suffix = root.replace(in_dir, "")
            for string_to_replace in flac_strings_to_replace:
                dir_suffix = dir_suffix.replace(string_to_replace, flac_str_replacement)
            dest_dir = out_dir + dir_suffix
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            if (os.path.splitext(filename)[1]) not in ".flac":
                print("copying: " + dest_dir + "/" + filename)
                shutil.copy2(root + "/" + filename, dest_dir + "/" + filename)

    # populate database
    _artist = None
    for (root,dirs,files) in os.walk(in_dir, topdown=True):
        for filename in files:
            if (os.path.splitext(filename)[1]) in ".flac":
                dir_suffix = root.replace(in_dir, "")
                full_path = in_dir + dir_suffix + "/" + filename
                try:
                    tag = TinyTag.get(full_path)
                    album = tag.album
                    # albumartist = tag.albumartist
                    artist = tag.artist
                    if tag.bitrate:
                        bitrate = int(tag.bitrate)
                    # comment = tag.comment
                    # disc = tag.disc
                    if tag.duration:
                        duration_s = int(tag.duration)
                    title = tag.title
                    if title == None:
                        file1 = open(error_log, "a")
                        file1.write(full_path + '\n' + "has no tags and will not be processed" + '\n\n')
                        file1.close()
                        break
                    track_num = tag.track
                    # year = tag.year
                    if artist and _artist != artist:
                        print("entering into database: " + artist + " " + album)
                        _artist = artist
                    query = 'INSERT OR IGNORE INTO tracks(artist, album, title, track_num, duration_s, bitrate, \
                    dir_suffix, filename) VALUES(?,?,?,?,?,?,?,?);'
                    c.execute(query, ( artist, album, title, track_num, duration_s, bitrate, dir_suffix, filename, ))
                    conn.commit()
                except Exception as e:
                    file1 = open(error_log, "a")
                    file1.write(full_path + '\n' + str(e) + '\n\n')
                    file1.close()


    if conn:
        conn.close()
    show_stats(db_path)
    print("\nREADY TO ENCODE\n")
