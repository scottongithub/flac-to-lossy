import sqlite3

def show_stats(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = 'SELECT duration_s FROM tracks'
    total_dur = c.execute(query)
    track_count = 0
    total_duration_s = 0
    for dur in total_dur:
        total_duration_s += int(dur[0])
        track_count += 1

    query = 'SELECT duration_s FROM tracks WHERE finished = 1 '
    finished_dur = c.execute(query)
    finished_duration_s = 0
    for dur in finished_dur:
        finished_duration_s += int(dur[0])


    query = 'SELECT duration_s, locktime_s, donetime_s from tracks WHERE finished = 1 and donetime_s IS NOT NULL ORDER BY id DESC LIMIT 50'
    rows = c.execute(query)
    rows = rows.fetchall()
    if len(rows) > 20: # don't show time left until there's enough data
        sample_duration_s = 0
        locktime_min = 9999999999
        donetime_max = 0
        for row in rows:
            sample_duration_s = sample_duration_s + int(row[0])
            if row[1] < locktime_min:
                locktime_min = row[1]
            if row[2] > donetime_max:
                donetime_max = row[2]
        track_encoding_duration = donetime_max - locktime_min
        current_rate = track_encoding_duration / sample_duration_s
        encoded_time_left_s = total_duration_s - finished_duration_s
        real_time_left_s = encoded_time_left_s * current_rate

    total_duration_h = int(total_duration_s / 3600)
    total_duration_d = (total_duration_h / 24)
    finished_percent = int((finished_duration_s / total_duration_s) * 100)

    print()
    print("total tracks:                " + str(track_count))
    print("track duration in hours:     " + str(total_duration_h))
    print("track duration in days:      " + str(round(total_duration_d, 1)))
    print("percent encoded (by time):   " + str(finished_percent))
    if 'real_time_left_s' in locals():
        print("real time left (s):          " + str(round(real_time_left_s)))
        print("real time left (m):          " + str(round(real_time_left_s / 60)))
        print("real time left (h):          " + str(round(real_time_left_s / 3600, 1)))
        print("rate over past " + str(len(rows)) + " tracks:    " + str(round(1 / current_rate)) + "x")
        # print("encoded time left (s):       " + str(total_duration_s - finished_duration_s))
    print()

    if conn:
        conn.close()

if __name__ == "__main__":
    show_stats(db_path)
