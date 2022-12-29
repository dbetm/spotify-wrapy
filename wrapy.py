from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

from constants import (
    DAYS_WEEK_MAP,
    TOTAL_SECONDS_PER_DAY,
    TOTAL_SECONDS_PER_HOUR,
    TOTAL_SECONDS_PER_MINUTE,
)

def generate_plays_days_of_week_map(
    data: pd.DataFrame,
    column_name: str = "endTime",
    date_format: str = "%Y-%m-%d %H:%M",
) -> List[tuple]:
    data = data.copy()
    data[column_name] =  pd.to_datetime(data[column_name], format=date_format)

    results = dict()

    for idx, row in data.iterrows():
        weekday_key = row[column_name].weekday()
        
        if not weekday_key in results:
            results[weekday_key] = 1
        else:
            results[weekday_key] += 1

    sorted_results = sorted(results.items())

    return sorted_results


def display_polar_graph(data: List[tuple], plot_title: str):
    labels = list()
    values = list()
    max_value = 0

    # set color theme
    plt.style.use("dark_background")

    for item in data:
        labels.append(DAYS_WEEK_MAP[item[0]])
        values.append(item[1])

        max_value = max(max_value, item[1])

    # Set the number of angles and the angles
    angles = np.linspace(start=0, stop=2*np.pi, num=len(labels), endpoint=False)

    # Set the figure size
    plt.figure(figsize=(8, 8))

    # Set the grid
    plt.grid(True)

    # Set the axes, 111 to create a single plot
    ax = plt.subplot(111, polar=True)

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
        day = labels[i]
        plt.text(
            x=angle,
            y=value - 100,
            s=f"{day}: {value}",
            ha="center",
            va="center",
            fontweight="semibold",
        )

    # Set the title and the font size
    plt.title(label=plot_title, fontsize=14)

    # Show the plot
    plt.show()


def compute_unique_values(data: pd.DataFrame, column_name: str) -> int:
    count = data[column_name].unique().size

    print(f"{column_name}: {count}")

    return count


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