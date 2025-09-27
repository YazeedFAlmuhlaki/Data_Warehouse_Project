import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events (
    event_id       BIGINT IDENTITY(1,1) PRIMARY KEY,
    artist         TEXT,
    auth           TEXT,
    firstName      TEXT,
    Gender         TEXT,
    itemInSession  INT,
    lastName       TEXT,
    length         FLOAT,
    level          TEXT,
    location       TEXT,
    method         TEXT,
    page           TEXT,
    registration   BIGINT,
    sessionId      INT,
    song           TEXT,
    status         INT,
    ts             BIGINT,
    userAgent      TEXT,
    userId         INT
)
DISTSTYLE KEY
DISTKEY (userId)
SORTKEY (ts);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs        INT,
    artist_id       TEXT,
    artist_latitude FLOAT,
    artist_longitude FLOAT,
    artist_location TEXT,
    artist_name     TEXT,
    song_id         TEXT,
    title           TEXT,
    duration        FLOAT,
    year            INT
)
DISTSTYLE EVEN;
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id   BIGINT IDENTITY(1,1) PRIMARY KEY,
    start_time    TIMESTAMP NOT NULL,
    user_id       INT NOT NULL,
    level         TEXT,
    song_id       TEXT,
    artist_id     TEXT,
    session_id    INT,
    location      TEXT,
    user_agent    TEXT
)
DISTSTYLE KEY
DISTKEY (user_id)
SORTKEY (start_time);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id    INT PRIMARY KEY,
    first_name TEXT,
    last_name  TEXT,
    gender     TEXT,
    level      TEXT
)
DISTSTYLE ALL;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
    song_id   TEXT PRIMARY KEY,
    title     TEXT,
    artist_id TEXT,
    year      INT,
    duration  FLOAT
)
DISTSTYLE ALL;
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR PRIMARY KEY,
    name      TEXT,
    location  TEXT,
    latitude  FLOAT,
    longitude FLOAT
)
DISTSTYLE ALL;
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
    start_time TIMESTAMP PRIMARY KEY,
    hour       INT,
    day        INT,
    week       INT,
    month      INT,
    year       INT,
    weekday    INT
)
DISTSTYLE ALL;
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events FROM {}
CREDENTIALS 'aws_iam_role={}'
JSON {}
REGION '{}'
TIMEFORMAT 'epochmillisecs'
MAXERROR 100;
""").format(config.get('S3', 'LOG_DATA'),
            config.get('IAM_ROLE', 'ARN'),
            config.get('S3', 'LOG_JSONPATH'),
            config.get('S3', 'REGION'))

staging_songs_copy = ("""
COPY staging_songs FROM {}
CREDENTIALS 'aws_iam_role={}'
JSON 'auto'
REGION '{}'
MAXERROR 100;
""").format(config.get('S3', 'SONG_DATA'),
            config.get('IAM_ROLE', 'ARN'),
            config.get('S3', 'REGION'))

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT
    TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
    se.userId AS user_id,   
    se.level AS level,
    ss.song_id AS song_id,
    ss.artist_id AS artist_id,
    se.sessionId AS session_id,
    se.location AS location,
    se.userAgent AS user_agent
FROM staging_events se
JOIN staging_songs ss
ON se.song = ss.title
AND se.artist = ss.artist_name
WHERE se.page = 'NextSong'
AND se.userId IS NOT NULL
AND ss.song_id IS NOT NULL;
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name,gender, level)
SELECT DISTINCT
    userId AS user_id,
    firstName AS first_name,
    lastName AS last_name,
    gender AS gender,
    level AS level
FROM staging_events
WHERE userId IS NOT NULL;
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT
    song_id AS song_id,
    title AS title,
    artist_id AS artist_id,
    year AS year,
    duration AS duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
    artist_id AS artist_id,
    artist_name AS name,
    artist_location AS location,
    artist_latitude AS latitude,
    artist_longitude AS longitude
FROM staging_songs
WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT
    TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
    EXTRACT(hour FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS hour,
    EXTRACT(day FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS day,
    EXTRACT(week FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS week,
    EXTRACT(month FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS month,
    EXTRACT(year FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS year,
    EXTRACT(weekday FROM (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second')) AS weekday
FROM staging_events se
WHERE se.page = 'NextSong'
  AND se.ts IS NOT NULL;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
