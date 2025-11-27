import argparse
import os
from datetime import date, datetime
from functools import partial
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from tzlocal import get_localzone_name

from wrapy.constants import (
    CARD_IMG_SIZE,
    COVER_BG_IMAGE_PATH,
    DAYS_WEEK_MAP,
    DAYS_WEEK_MAP_EN,
    DEFAULT_OUTPUT_PATH,
    END_LOCAL_TIME_COL_NAME,
    K_TOP_SONGS,
    K_TOP_SONGS_GRAPH,
    LIMIT_DATE_FORMAT,
    REPO_URL,
    VIDEO_DIMENSIONS,
)
from wrapy.core import (
    calculate_human_total_play,
    compute_unique_values,
    count_song_skips,
    create_and_save_text_card,
    create_and_save_title_card,
    create_bar_graph,
    create_polar_graph,
    create_simple_plot,
    gen_top_k_graph,
    generate_n_star_viz,
    generate_plays_to_x_map,
    get_average_plays_per_day,
    get_period,
    get_top_artists,
    get_top_songs,
    get_top_songs_for_each_hour,
)
from wrapy.custom_exceptions import ValidationError
from wrapy.lang import EnLocale, EsLocale
from wrapy.logger_ import load_logger
from wrapy.utils import (
    convert_column_utc_datetime_to_local_time,
    filter_data_by_dates,
    load_streaming_history_data,
    map_int_day_to_weekday_name,
    parse_str_to_date,
    separate_di_tuples_in_two_lists,
    write_text_lines_in_new_text_file,
)
from wrapy.video.maker import VideoMaker


def setup_matplotlib(dark_theme: bool = True):
    if dark_theme:
        plt.style.use("dark_background")


def setup(lang: str):
    setup_matplotlib()

    global logger
    logger = load_logger()

    global locale
    locale = EnLocale() if lang == "english" else EsLocale()


def generate_and_save_stats(data: pd.DataFrame, output_path: str) -> list:
    total_plays = data.shape[0]

    song_skips_dict = count_song_skips(data)
    avg_plays_per_day = get_average_plays_per_day(data)
    avg_plays_per_day = str(round(avg_plays_per_day))
    total_song_skips = song_skips_dict.get("total", "ERROR")
    percentage_song_skips = song_skips_dict.get("percentage", "ERROR")

    start_date = data[END_LOCAL_TIME_COL_NAME].min().strftime("%Y/%m/%d")
    end_date = data[END_LOCAL_TIME_COL_NAME].max().strftime("%Y/%m/%d")
    time_period = f"{start_date} - {end_date}"

    if percentage_song_skips != "ERROR":
        percentage_song_skips = "{:.2f}".format(percentage_song_skips) + "%"

    human_total_play = calculate_human_total_play(data)
    played_days = human_total_play["days"]
    played_hours = human_total_play["hours"]
    played_minutes = human_total_play["minutes"]

    different_artists_listened = compute_unique_values(data, column_name="artistName")
    different_songs_played = compute_unique_values(data, column_name="trackName")

    is_plural = lambda unity: int(unity) > 1

    text_stats = [
        f"{locale.get_attr('total_play')}: {total_plays}",
        f"{locale.get_attr('song_skips')}: {total_song_skips}, {percentage_song_skips}",
        f"{locale.get_attr('avg_plays_per_day')}: {avg_plays_per_day}",
        f"{locale.get_attr('different_songs_listened')}: {different_songs_played}",
        (
            f"{locale.get_attr('total_play_listened')}:"
            f" {played_days} {locale.get_attr('day', is_plural(played_days))},"
            f" {played_hours} {locale.get_attr('hour', is_plural(played_hours))},"
            f" {played_minutes} {locale.get_attr('minute', is_plural(played_minutes))}"
        ),
        f"{locale.get_attr('different_artists_listened')}: {different_artists_listened}",
        f"{locale.get_attr('time_period')}: {time_period}",
    ]

    write_text_lines_in_new_text_file(text_stats, filepath=output_path)

    return text_stats


def validate_dates(start_date: date, end_date: date):
    if not (start_date and end_date):
        return

    if (start_date and not end_date) or (end_date and not start_date):
        logger.error("You must pass both dates: start-date and end-date")
        raise ValidationError

    if start_date > end_date:
        logger.error("start-date must be less than end-date")
        raise ValidationError

    logger.info(f"start-date given: {start_date}, end-date given: {end_date}")


def make_video(output_path_dir: str, text_stats: List[str], period: str) -> None:
    # create card for intro
    intro_card_path = os.path.join(output_path_dir, "00_intro.png")
    create_and_save_title_card(
        f"My Spotify Wrapy \n\n{period}",
        intro_card_path,
        CARD_IMG_SIZE,
        font_size=30,
        background_img=Image.open(COVER_BG_IMAGE_PATH).convert("RGB"),
    )
    # create card for stats
    stats_card_path = os.path.join(output_path_dir, "05_stats.png")
    create_and_save_text_card(
        "Stats",
        text_stats,
        CARD_IMG_SIZE,
        stats_card_path,
        title_font_size=30,
        content_font_size=18,
    )
    # create card for credits
    credits_card_path = os.path.join(output_path_dir, "z10_credits.png")
    create_and_save_title_card(
        f"{locale.get_attr('download_from')}\n\n{REPO_URL}\n\n\n+)",
        credits_card_path,
        CARD_IMG_SIZE,
        font_size=26,
    )

    image_paths = [
        os.path.join(output_path_dir, f)
        for f in os.listdir(output_path_dir)
        if f.endswith(".png")
    ]

    image_paths.sort()

    VideoMaker(image_paths, VIDEO_DIMENSIONS).make(
        output_path=os.path.join(output_path_dir, "my_wrapy.mp4")
    )


def run(
    local_timezone: str,
    start_date: date = None,
    end_date: date = None,
    create_video: bool = True,
):
    data = load_streaming_history_data()

    data = convert_column_utc_datetime_to_local_time(
        data=data,
        new_tz=local_timezone,
        column_name="endTime",
        new_column_name=END_LOCAL_TIME_COL_NAME,
    )

    if start_date and end_date:
        data = filter_data_by_dates(data, END_LOCAL_TIME_COL_NAME, start_date, end_date)

        if data.shape[0] < 2:
            logger.error("Too few records to generate stats")
            exit(0)

    new_folder = datetime.now().strftime("%Y-%m-%d %H_%M")
    output_path_dir = os.path.join(DEFAULT_OUTPUT_PATH, new_folder)

    if not os.path.exists(output_path_dir):
        os.mkdir(output_path_dir)

    # Stats
    text_stats = generate_and_save_stats(
        data, os.path.join(output_path_dir, "stats.txt")
    )
    logger.info("Stats generated")

    # Text cards
    plays_per_groups = generate_plays_to_x_map(
        data=data,
        target_names={"hour", "month", "weekday"},
        column_name=END_LOCAL_TIME_COL_NAME,
    )
    plays_per_hour = plays_per_groups["hour"]

    # top songs
    top_songs = get_top_songs(data, k_top=K_TOP_SONGS)
    top_5_songs = top_songs.head(5).to_dict(orient="records")
    create_and_save_text_card(
        locale.get_attr("top_songs_card_title"),
        [
            f"{song['trackName'][:35]} - {song['artistName'][:35]}: {song['plays']}"
            for song in top_5_songs
        ],
        CARD_IMG_SIZE,
        os.path.join(output_path_dir, "06_top_songs.png"),
        title_font_size=25,
        content_font_size=18,
    )

    # top songs for each hour (from a top 5)
    top_songs_for_top_hours = get_top_songs_for_each_hour(
        data, plays_per_hour, 5, "endLocalTime", join_word=locale.get_attr("by")
    )
    top_songs_for_top_hours = dict(sorted(top_songs_for_top_hours.items()))
    create_and_save_text_card(
        locale.get_attr("top_songs_for_top_hours_card_title"),
        [
            f"{song} {locale.get_attr('at_time')} {hour}h"
            for hour, song in top_songs_for_top_hours.items()
        ],
        CARD_IMG_SIZE,
        os.path.join(output_path_dir, "09_top_songs_for_top_hours.png"),
        title_font_size=25,
        content_font_size=18,
    )

    # top artists
    top_artists = get_top_artists(data, 5)
    create_and_save_text_card(
        locale.get_attr("top_artists_card_title"),
        [
            f"{artist}: {plays} {locale.get_attr('play')}"
            for artist, plays in top_artists.items()
        ],
        CARD_IMG_SIZE,
        os.path.join(output_path_dir, "07_top_artists.png"),
        title_font_size=24,
        content_font_size=21,
    )

    logger.info("Text cards generated")

    # Plots

    # accumulated plays per day of the week
    plays_per_weekday = plays_per_groups["weekday"]
    days_week_map = DAYS_WEEK_MAP_EN if isinstance(locale, EnLocale) else DAYS_WEEK_MAP

    create_polar_graph(
        data=plays_per_weekday,
        plot_title=locale.get_attr("plays_per_weekday_plot_title"),
        label_map_fn=partial(map_int_day_to_weekday_name, days_week_map),
        save_path=os.path.join(output_path_dir, "03_plays_per_weekday.png"),
        title_font_size=20,
    )
    # accumulated plays per hour
    x_hours, y_hour_values = separate_di_tuples_in_two_lists(plays_per_hour)
    create_bar_graph(
        x=x_hours,
        y=y_hour_values,
        plot_title=locale.get_attr("plays_per_hour_plot_title"),
        x_label=locale.get_attr("hour"),
        save_path=os.path.join(output_path_dir, "01_plays_per_hour.png"),
        title_font_size=20,
    )
    # accumulated plays per month - simple plot
    plays_per_month = plays_per_groups["month"]
    x_months, y_month_value = separate_di_tuples_in_two_lists(plays_per_month)
    create_simple_plot(
        x=x_months,
        y=y_month_value,
        plot_title=locale.get_attr("plays_per_month_plot_title"),
        x_label=locale.get_attr("month"),
        save_path=os.path.join(output_path_dir, "02_plays_per_month.png"),
        title_font_size=20,
    )

    generate_n_star_viz(
        top_songs,
        img_size=CARD_IMG_SIZE[::-1],
        title=locale.get_attr("artists_color_coded_from_top_songs").format(
            K=K_TOP_SONGS
        ),
        save_path=os.path.join(
            output_path_dir, "04_star_with_artists_color_coded_from_top_songs.png"
        ),
    )

    gen_top_k_graph(
        data=data,
        img_size=CARD_IMG_SIZE,
        title=locale.get_attr("play_history_from_top_songs").format(
            K=K_TOP_SONGS_GRAPH
        ),
        save_path=os.path.join(output_path_dir, "08_top_songs_history_graph.png"),
        k_top=K_TOP_SONGS_GRAPH,
    )

    logger.info("Plots generated")

    if create_video:
        logger.info("Generating video...")
        make_video(
            output_path_dir=output_path_dir,
            text_stats=text_stats,
            period=get_period(data, "endLocalTime"),
        )

    logger.info(f"Done, checkout the folder: {output_path_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tz", type=str, required=False, default=get_localzone_name())
    parser.add_argument(
        "--start-date",
        type=parse_str_to_date,
        required=False,
        default=None,
        help=f"Format to use: {LIMIT_DATE_FORMAT}",
    )
    parser.add_argument(
        "--end-date",
        type=parse_str_to_date,
        required=False,
        default=None,
        help=f"Format to use: {LIMIT_DATE_FORMAT}",
    )
    parser.add_argument(
        "--lang",
        choices=["spanish", "english"],
        required=False,
        default="english",
        help="Language to use for the stats and plots",
    )
    parser.add_argument("--no-video", action="store_false", help="no generate video")
    args = parser.parse_args()
    timezone_name = args.tz

    setup(args.lang)

    if not timezone_name:
        logger.warning(
            "Timezone can't be determined, using 'America/Mexico_City' by default"
        )
    else:
        logger.info(f"Using timezone: {timezone_name}")

    validate_dates(args.start_date, args.end_date)

    run(
        local_timezone=timezone_name,
        start_date=args.start_date,
        end_date=args.end_date,
        create_video=args.no_video,
    )
