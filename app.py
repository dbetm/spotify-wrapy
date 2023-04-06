import argparse
import logging
import os
from functools import partial
from datetime import datetime
import sys

import matplotlib.pyplot as plt
import pandas as pd

from constants import DEFAULT_OUTPUT_PATH
from utils import (
    get_local_timezone_name,
    load_streaming_history_data,
    map_int_day_to_weekday_name,
    separate_di_tuples_in_two_lists,
    write_text_lines_in_new_text_file,
)
from wrapy import (
    calculate_human_total_play,
    compute_unique_values,
    count_song_skips,
    create_bar_graph,
    create_polar_graph,
    create_simple_plot,
    get_average_plays_per_day,
    generate_plays_to_x_map,
)


def setup_matplotlib(dark_theme: bool = True):
    if dark_theme:
        plt.style.use("dark_background")


def setup():
    setup_matplotlib()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    global logger
    logger = logging.getLogger()


def generate_and_save_stats(data: pd.DataFrame, output_path: str):
    total_plays = data.shape[0]

    song_skips_dict = count_song_skips(data)
    avg_plays_per_day = get_average_plays_per_day(data)
    avg_plays_per_day = "{:.2f}".format(avg_plays_per_day)
    total_song_skips = song_skips_dict.get("total", "ERROR")
    percentage_song_skips = song_skips_dict.get("percentage", "ERROR")

    if percentage_song_skips != "ERROR":
        percentage_song_skips = "{:.2f}".format(percentage_song_skips) + "%"

    human_total_play = calculate_human_total_play(data)
    played_days = human_total_play["days"]
    played_hours = human_total_play["hours"]
    played_minutes = human_total_play["minutes"]

    different_artists_listened = compute_unique_values(data, column_name="artistName")
    different_songs_played = compute_unique_values(data, column_name="trackName")

    write_text_lines_in_new_text_file(
        [
            f"Total de reproducciones: {total_plays}",
            f"Canciones saltadas: {total_song_skips}, {percentage_song_skips}",
            f"Reproducciones promedio por día: {avg_plays_per_day}",
            (
                f"Tiempo total escuchado: {played_days} día(s), {played_hours} hora(s) y"
                f" {played_minutes} minuto(s)."
            ),
            f"Artistas diferentes escuchados: {different_artists_listened}",
            f"Canciones diferentes escuchadas: {different_songs_played}",
        ],
        filepath=output_path,
    )


def run(local_timezone: str):
    data = load_streaming_history_data()

    new_folder = datetime.now().strftime("%Y-%m-%d %H_%M")
    output_path_dir = os.path.join(DEFAULT_OUTPUT_PATH, new_folder)

    if not os.path.exists(output_path_dir):
        os.mkdir(output_path_dir)

    # Stats
    generate_and_save_stats(data, output_path_dir + "/" + "stats.txt")
    logger.info("Stats generated")

    # Plots
    generate_plays_map_partial = partial(
        generate_plays_to_x_map, data=data, local_timezone=local_timezone
    )
    # accumulated plays per day of the week
    plays_per_weekday = generate_plays_map_partial(x_target="weekday")
    create_polar_graph(
        data=plays_per_weekday,
        plot_title="Reproducciones por día de la semana",
        label_map_fn=map_int_day_to_weekday_name,
        save_path=output_path_dir + "/" + "plays_per_weekday.png",
    )
    # accumulated plays per hour
    plays_per_hour = generate_plays_map_partial(x_target="hour")
    x_hours, y_hour_values = separate_di_tuples_in_two_lists(plays_per_hour)
    create_bar_graph(
        x=x_hours,
        y=y_hour_values,
        plot_title="Reproducciones por hora",
        x_label="hora",
        save_path=output_path_dir + "/" + "plays_per_hour.png",
    )
    # accumulated plays per month - simple plot
    plays_per_month = generate_plays_map_partial(x_target="month")
    x_months, y_month_value = separate_di_tuples_in_two_lists(plays_per_month)
    create_simple_plot(
        x=x_months,
        y=y_month_value,
        plot_title="Reproducciones por mes",
        x_label="mes",
        save_path=output_path_dir + "/" + "plays_per_month.png",
    )

    logger.info("Plots generated")
    logger.info(f"Done, checkout the folder: {output_path_dir}/")


if __name__  == "__main__":
    setup()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tz", type=str, required=False, default=get_local_timezone_name()
    )
    args = parser.parse_args()
    logger.warning(f"Using timezone: {args.tz}")

    run(local_timezone=args.tz)