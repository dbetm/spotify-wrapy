from typing import Callable, List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joypy import joyplot
from matplotlib import cm

from constants import (
    TOTAL_SECONDS_PER_DAY,
    TOTAL_SECONDS_PER_HOUR,
    TOTAL_SECONDS_PER_MINUTE,
)
from utils import convert_column_utc_datetime_to_local_time


def generate_plays_days_of_week_map(
    data: pd.DataFrame,
    local_timezone: str,
    column_name: str = "endTime",
    date_format: str = "%Y-%m-%d %H:%M",
) -> List[tuple]:
    data = data.copy()

    data = convert_column_utc_datetime_to_local_time(
        data=data,
        new_tz=local_timezone,
        column_name=column_name,
        date_format=date_format,
    )

    results = dict()

    for idx, row in data.iterrows():
        weekday_key = row[column_name].weekday()
        
        if not weekday_key in results:
            results[weekday_key] = 1
        else:
            results[weekday_key] += 1

    sorted_results = sorted(results.items())

    return sorted_results


def generate_plays_hour_day_map(
    data: pd.DataFrame,
    local_timezone: str,
    column_name: str = "endTime",
    date_format: str = "%Y-%m-%d %H:%M",
) -> List[tuple]:
    data = data.copy()

    data = convert_column_utc_datetime_to_local_time(
        data=data,
        new_tz=local_timezone,
        column_name=column_name,
        date_format=date_format,
    )

    results = dict()

    for _, row in data.iterrows():
        hour = row[column_name].hour
        
        if not hour in results:
            results[hour] = 1
        else:
            results[hour] += 1

    sorted_results = sorted(results.items())

    return sorted_results


def generate_plays_month_map(
    data: pd.DataFrame,
    local_timezone: str,
    column_name: str = "endTime",
    date_format: str = "%Y-%m-%d %H:%M",
) -> List[tuple]:
    data = data.copy()

    data = convert_column_utc_datetime_to_local_time(
        data=data,
        new_tz=local_timezone,
        column_name=column_name,
        date_format=date_format,
    )

    results = dict()

    for _, row in data.iterrows():
        month = row[column_name].month
        
        if not month in results:
            results[month] = 1
        else:
            results[month] += 1

    sorted_results = sorted(results.items())

    return sorted_results


def display_polar_graph(
    data: List[tuple],
    plot_title: str,
    label_map_fn: Callable = lambda x : x,
):
    labels = list()
    values = list()
    max_value = 0

    # set color theme
    plt.style.use("dark_background")

    for item in data:
        labels.append(label_map_fn(item[0]))
        values.append(item[1])

        max_value = max(max_value, item[1])

    # Set the number of angles and the angles
    angles = np.linspace(start=0, stop=2*np.pi, num=len(labels), endpoint=False)

    # Set the figure size
    plt.figure(figsize=(8, 8))

    # Set the axes, 111 to create a single plot
    ax = plt.subplot(111, polar=True)
    ax.grid(visible=True, alpha=0.6, linewidth=1)

    # set color style
    color_map = cm.get_cmap("winter")

    # Set the bar plot
    ax.bar(
        angles,
        values,
        width=(2*np.pi) / len(labels),
        bottom=0.0,
        color=color_map(list(np.array(values) / max_value))
    )

    # set labels
    ax.set_xticks(angles)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Add the values over the slices
    for i, value in enumerate(values):
        angle = angles[i]
        label = labels[i]
        plt.text(
            x=angle,
            y=value - 100,
            s=f"{label}: {value}",
            ha="center",
            va="center",
            fontweight="semibold",
        )

    # Set the title and the font size
    plt.title(label=plot_title, fontsize=14, pad=20)

    # Show the plot
    plt.show()


def compute_unique_values(data: pd.DataFrame, column_name: str) -> int:
    count = data[column_name].unique().size

    print(f"{column_name}: {count}")

    return count


def count_song_skips(data: pd.DataFrame, ms_tolerance: int = 10_000) -> dict:
    jumps = data[data["msPlayed"] < ms_tolerance].shape[0]
    jumps_percentage = (jumps / data.shape[0]) * 100.0

    return {"percentage": jumps_percentage, "total": jumps}


def display_bar_graph(
    x: List[Union[int, str]],
    y: List[int],
    plot_title: str,
    x_label: str,
):
    max_value = max(y)

    # Set the figure size, width and heigh in inches
    plt.rcParams["figure.figsize"] = (10, 5)

    # set color theme
    plt.style.use("dark_background")

    # set color palette
    color_map = cm.get_cmap("winter")

    # create plot
    fig, ax = plt.subplots()

    ax.bar(
        x=x,
        height=y,
        tick_label=x,
        color=color_map(list(np.array(y) / max_value))
    )

    # add title and labels
    ax.set_title(label=plot_title)
    ax.set_xlabel(xlabel=x_label)
    ax.set_ylabel(ylabel="Plays")

    fig.tight_layout()


def display_simple_plot(
    x: List[Union[str, int]], y: List[int], plot_title: str, x_label: str
):
    # set color theme
    plt.style.use("dark_background")

    # Set the figure size
    plt.figure(figsize=(8, 8))

    # plot
    plt.plot(x, y, color="#86C8BC", linewidth=3)
    plt.xticks(x)
    plt.grid(True, linewidth=1, alpha=0.4)
    
    # title and labels
    plt.title(label=plot_title)
    plt.xlabel(xlabel=x_label)
    plt.ylabel(ylabel="plays")

    plt.show()


def calculate_human_total_play(
    data: pd.DataFrame, column_name = "msPlayed"
) -> dict:
    total_ms = data[column_name].sum()
    ms_per_day = (TOTAL_SECONDS_PER_DAY * 1000)
    ms_per_hour = (TOTAL_SECONDS_PER_HOUR * 1000)
    ms_per_minute = (TOTAL_SECONDS_PER_MINUTE * 1000)

    # days
    total_days = total_ms // ms_per_day
    total_ms = total_ms % ms_per_day
    # hours
    total_hours = total_ms // ms_per_hour
    total_ms = total_ms % ms_per_hour
    # minutes
    total_minutes = total_ms // ms_per_minute

    return {"days": total_days, "hours": total_hours, "minutes": total_minutes}