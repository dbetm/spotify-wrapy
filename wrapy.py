from typing import Callable, List, Optional, Set, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

from constants import (
    ALLOWED_X_TARGETS,
    DAYS_PER_YEAR,
    TOTAL_SECONDS_PER_DAY,
    TOTAL_SECONDS_PER_HOUR,
    TOTAL_SECONDS_PER_MINUTE,
)


def __increase_key_group(groups: dict, group_name: str, key: str) -> dict:
    """Increase accumulator by given group name and key of that group."""
    assert group_name in groups

    if not key in groups[group_name]:
        groups[group_name][key] = 1
    else:
        groups[group_name][key] += 1

    return groups


def generate_plays_to_x_map(
    data: pd.DataFrame,
    target_names: Set[str],
    column_name: str = "endLocalTime",
) -> List[tuple]:

    for target_name in target_names:
        assert target_name in ALLOWED_X_TARGETS

    groups = {"hour": dict(), "weekday": dict(), "month": dict()}

    for _, row in data.iterrows():
        if "hour" in target_names:
            key_hour = row[column_name].hour
            groups = __increase_key_group(
                groups, group_name="hour", key=key_hour
            )
        if "weekday" in target_names:
            key_weekday = row[column_name].weekday()
            groups = __increase_key_group(
                groups, group_name="weekday", key=key_weekday
            )
        if "month" in target_names:
            key_month = row[column_name].month
            groups = __increase_key_group(
                groups, group_name="month", key=key_month
            )

    for group_name, results in groups.items():
        groups[group_name] = sorted(results.items())

    return groups


def compute_unique_values(data: pd.DataFrame, column_name: str) -> int:
    count = data[column_name].unique().size

    return count


def count_song_skips(data: pd.DataFrame, ms_tolerance: int = 10_000) -> dict:
    jumps = data[data["msPlayed"] < ms_tolerance].shape[0]
    jumps_percentage = (jumps / data.shape[0]) * 100.0

    return {"percentage": jumps_percentage, "total": jumps}


def get_average_plays_per_day(data: pd.DataFrame, ms_tolerance: int = 10_000) -> float:
    plays_without_jumps = data[data["msPlayed"] >= ms_tolerance].shape[0]

    return plays_without_jumps / DAYS_PER_YEAR


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


def create_polar_graph(
    data: List[tuple],
    plot_title: str,
    label_map_fn: Callable = lambda x : x,
    save_path: Optional[str] = None,
):
    labels = list()
    values = list()
    max_value = 0

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
    ax.grid(visible=True, alpha=0.7, linewidth=1.5)

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

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        # Show the plot
        plt.show()


def create_bar_graph(
    x: List[Union[int, str]],
    y: List[int],
    plot_title: str,
    x_label: str,
    save_path: Optional[str] = None,
):
    max_value = max(y)

    # Set the figure size, width and heigh in inches
    plt.rcParams["figure.figsize"] = (10, 5)

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
    plt.title(label=plot_title, fontsize=14, pad=20)
    ax.set_xlabel(xlabel=x_label)
    ax.set_ylabel(ylabel="Plays")

    fig.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def create_simple_plot(
    x: List[Union[str, int]],
    y: List[int],
    plot_title: str,
    x_label: str,
    save_path: Optional[str] = None,
):
    # Set the figure size
    plt.figure(figsize=(8, 8))

    # plot
    plt.plot(x, y, color="#86C8BC", linewidth=3)
    plt.xticks(x)
    plt.grid(True, linewidth=1, alpha=0.4)
    
    # title and labels
    plt.title(label=plot_title, fontsize=14, pad=20)
    plt.xlabel(xlabel=x_label)
    plt.ylabel(ylabel="plays")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
