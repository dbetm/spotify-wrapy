import os

DEFAULT_DATA_DIR = "spotify_data"
DEFAULT_OUTPUT_PATH = "output"
ASSETS_PATH = "assets"

TOTAL_SECONDS_PER_DAY = 86400
TOTAL_SECONDS_PER_HOUR = 3600
TOTAL_SECONDS_PER_MINUTE = 60
DAYS_PER_YEAR = 365.0
LIMIT_DATE_FORMAT = "%Y-%m-%d"
K_TOP_SONGS = 20

DAYS_WEEK_MAP_EN = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

DAYS_WEEK_MAP = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sabádo",
    6: "Domingo",
}

ALLOWED_X_TARGETS = {"month", "weekday", "hour"}

END_LOCAL_TIME_COL_NAME = "endLocalTime"

REPO_URL = "https://github.com/dbetm/spotify-wrapy"

# Video generation
VIDEO_DIMENSIONS = (1920, 1080)
IMAGE_DURATION_SECS = 3.66
FPS = 30
TRANSTITION_DURATION_SECS = 0.6

# Text cards
CARD_IMG_SIZE = VIDEO_DIMENSIONS
COVER_BG_IMAGE_PATH = os.path.join(ASSETS_PATH, "earth-from-iss-for-cover.png")
