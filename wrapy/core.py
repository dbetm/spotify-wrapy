import math
import random
from typing import Callable, List, Optional, Set, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import cm
from PIL import Image, ImageDraw, ImageFont

from wrapy.constants import (
    ALLOWED_X_TARGETS,
    DAYS_PER_YEAR,
    TOTAL_SECONDS_PER_DAY,
    TOTAL_SECONDS_PER_HOUR,
    TOTAL_SECONDS_PER_MINUTE,
)

GREEN_BLUE_HEXA_COLOR = "#86C8BC"
WHITE_COLOR = "#ffffff"


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
            groups = __increase_key_group(groups, group_name="hour", key=key_hour)
        if "weekday" in target_names:
            key_weekday = row[column_name].weekday()
            groups = __increase_key_group(groups, group_name="weekday", key=key_weekday)
        if "month" in target_names:
            key_month = row[column_name].month
            groups = __increase_key_group(groups, group_name="month", key=key_month)

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


def get_top_songs(
    data: pd.DataFrame,
    k_top: int = 5,
    song_column: str = "trackName",
    artist_column: str = "artistName",
) -> pd.DataFrame:
    """Get the most listened songs."""
    song_id_key = "song_id"
    data[song_id_key] = data[song_column] + "#&&6" + data[artist_column]
    song_counts = data[song_id_key].value_counts(ascending=False).head(k_top)

    df = song_counts.index.to_series().str.extract(r"^(.*?)#&&6(.*)$")
    df.columns = [song_column, artist_column]

    df["plays"] = song_counts.values

    return df.reset_index().drop(columns=[song_id_key])


def get_top_artists(
    data: pd.DataFrame, k_top: int = 5, artist_column: str = "artistName"
) -> pd.DataFrame:
    """Get the most listened artists."""
    return data[artist_column].value_counts(ascending=False).head(k_top)


def get_top_songs_for_each_hour(
    data: pd.DataFrame,
    plays_per_hour: List[tuple],
    k_top: int = 5,
    timestamp_col: str = "endTime",
    song_col: str = "trackName",
    artist_column: str = "artistName",
    join_word: str = "",
) -> dict:
    """Return a dictionary mapping top hour with top song + artist"""
    plays_per_hour.sort(key=lambda x: x[1], reverse=True)

    top_hours = [hour for hour, _ in plays_per_hour[:k_top]]
    top_songs_for_each_hour = dict()

    for hour in top_hours:
        data_by_hour = data[data[timestamp_col].dt.hour == hour]
        top_song = data_by_hour[song_col].value_counts(ascending=False).index[0]
        artist = data[data[song_col] == top_song].iloc[0].to_dict()[artist_column]

        top_songs_for_each_hour[hour] = f"{top_song} {join_word} {artist}"

    return top_songs_for_each_hour


def calculate_human_total_play(data: pd.DataFrame, column_name="msPlayed") -> dict:
    total_ms = data[column_name].sum()
    ms_per_day = TOTAL_SECONDS_PER_DAY * 1000
    ms_per_hour = TOTAL_SECONDS_PER_HOUR * 1000
    ms_per_minute = TOTAL_SECONDS_PER_MINUTE * 1000

    # days
    total_days = total_ms // ms_per_day
    total_ms = total_ms % ms_per_day
    # hours
    total_hours = total_ms // ms_per_hour
    total_ms = total_ms % ms_per_hour
    # minutes
    total_minutes = total_ms // ms_per_minute

    return {"days": total_days, "hours": total_hours, "minutes": total_minutes}


def get_period(data: pd.DataFrame, column_name: str = "endTime") -> str:
    """Get from data the minimum date and maximum dates as a period as formatted string."""
    return (
        f"{data[column_name].min().strftime('%b/%Y')}"
        f"  -  {data[column_name].max().strftime('%b/%Y')}"
    )


def create_polar_graph(
    data: List[tuple],
    plot_title: str,
    label_map_fn: Callable = lambda x: x,
    save_path: Optional[str] = None,
    title_font_size: int = 14,
):
    labels = list()
    values = list()
    max_value = 0

    for item in data:
        labels.append(label_map_fn(item[0]))
        values.append(item[1])

        max_value = max(max_value, item[1])

    # Set the number of angles and the angles
    angles = np.linspace(start=0, stop=2 * np.pi, num=len(labels), endpoint=False)

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
        width=(2 * np.pi) / len(labels),
        bottom=0.0,
        color=color_map(list(np.array(values) / max_value)),
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
            fontsize="medium",
        )

    # Set the title and the font size
    plt.title(
        label=plot_title,
        fontsize=title_font_size,
        pad=20,
        color=WHITE_COLOR,
        weight="bold",
    )

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
    title_font_size: int = 14,
):
    max_value = max(y)

    # Set the figure size, width and heigh in inches
    plt.rcParams["figure.figsize"] = (10, 10)

    # set color palette
    color_map = cm.get_cmap("winter")

    # create plot
    fig, ax = plt.subplots()

    ax.bar(x=x, height=y, tick_label=x, color=color_map(list(np.array(y) / max_value)))

    # add title and labels
    plt.title(
        label=plot_title,
        fontsize=title_font_size,
        pad=20,
        color=WHITE_COLOR,
        weight="bold",
    )
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
    y_label: str = "plays",
    save_path: Optional[str] = None,
    title_font_size: int = 14,
):
    # Set the figure size
    plt.figure(figsize=(8, 8))

    # plot
    plt.plot(x, y, color=GREEN_BLUE_HEXA_COLOR, linewidth=3)
    plt.xticks(x)
    plt.grid(True, linewidth=1, alpha=0.4)

    # title and labels
    plt.title(
        label=plot_title,
        fontsize=title_font_size,
        pad=20,
        color=WHITE_COLOR,
        weight="bold",
    )
    plt.xlabel(xlabel=x_label)
    plt.ylabel(ylabel=y_label)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def create_and_save_text_card(
    title: str,
    text_lines: str,
    img_size: tuple,
    save_path: str,
    title_font_size: int = 20,
    content_font_size: int = 14,
) -> None:
    dots_per_inch = 200
    width = img_size[1] / 100  # Divide by DPI to get size in inches
    height = img_size[0] / 100  # Divide by DPI to get size in inches

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(width, height), dpi=dots_per_inch)

    assert len(text_lines) < 10, "text_lines must be contains less than 10 strings"

    # Remove axis and ticks
    ax.axis("off")

    # Define the initial Y position and their delta
    y = 0.85
    delta = 0.10

    # Add the title with center alignment
    ax.text(
        x=0.5,
        y=y,
        s=title,
        ha="center",
        fontsize=title_font_size,
        color=GREEN_BLUE_HEXA_COLOR,
        weight="bold",
    )
    # Update the Y position for the next line
    y -= 0.15

    # Add each line of text
    for line in text_lines:
        ax.text(x=0.5, y=y, s=line, ha="center", fontsize=content_font_size)
        y -= delta

    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def create_and_save_title_card(
    title: str,
    save_path: str,
    img_size: tuple,
    font_size: int = 16,
    background_img: Optional[Image.Image] = None,
) -> None:
    """Create card as an image, containing only a title centered."""
    dots_per_inch = 100
    width = img_size[1] / dots_per_inch  # Divide by DPI to get size in inches
    height = img_size[0] / dots_per_inch  # Divide by DPI to get size in inches

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(width, height), dpi=dots_per_inch)
    # remove internal margins / borders
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Remove axis and ticks
    ax.axis("off")

    if background_img is not None:
        bg = background_img.resize((img_size[1], img_size[0]))
        # [xmin, xmax, ymin, ymax] / 0 is the left botton border and 1 is right/upper
        ax.imshow(bg, extent=[0, 1, 0, 1], aspect="auto")

    # Add the title with center alignment
    ax.text(
        x=0.5,
        y=0.5,
        s=title,
        ha="center",
        fontsize=font_size,
        color=WHITE_COLOR,
        weight="bold",
    )

    plt.savefig(save_path, dpi=dots_per_inch)
    plt.close(fig)


def generate_n_star_viz(
    data: pd.DataFrame, img_size: tuple, title: str, save_path: str
) -> None:
    """Create an image with an n star color coded from the artists
    from the tops songs listened to. The number of spikes is equal to the number of records.
    """
    n = data.shape[0]
    color_padding_dark = 70
    color_padding_light = 10
    img_padding = 5
    random.seed(42)

    def get_random_color():
        return tuple(
            random.randint(0 + color_padding_dark, 255 - color_padding_light)
            for _ in range(3)
        )

    colors_map = dict()
    colors = list()

    for _, row in data.iterrows():
        if row["artistName"] in colors_map:
            colors.append(colors_map[row["artistName"]])
        else:
            new_color = get_random_color()
            colors_map[row["artistName"]] = new_color
            colors.append(new_color)

    width, height = img_size
    center = ((width - img_padding) // 2, (height - img_padding) // 2)
    radius_outer = min(center) - 20  # Outer radius
    radius_inner = (radius_outer // 2) - 35  # Inner radius

    angle_step = 360 / n  # Degrees between points

    # Create a base image with a black background
    image = Image.new("RGB", img_size, "black")
    draw = ImageDraw.Draw(image)

    points = []
    for i in range(n * 2):
        angle_deg = angle_step * (i / 2)
        angle_rad = (angle_deg / 180) * np.pi
        radius = radius_outer if i % 2 == 0 else radius_inner
        x = int(center[0] + radius * math.cos(angle_rad))
        y = int(center[1] + radius * math.sin(angle_rad))
        points.append((x, y))

    # Draw each spike with random colors
    for i in range(len(points)):
        spike_color = colors[(i + 1) // 2 % len(colors)]
        draw.polygon(
            [center, points[i], points[(i + 1) % len(points)]],
            fill=spike_color,
            outline=None,
        )

    # Put text title
    font = ImageFont.load_default(size=50)
    # Step 5: Draw the text on the image
    draw.text((100, 200), title, fill=WHITE_COLOR, font=font)

    image.save(save_path)


def gen_top_k_graph(
    data: pd.DataFrame,
    img_size: tuple,
    title: str,
    save_path: str,
    k_top: int = 15,
    song_column: str = "trackName",
    artist_column: str = "artistName",
) -> None:
    song_id_key = "song_id"
    data[song_id_key] = data[song_column] + "\n" + data[artist_column]

    data["endTime"] = pd.to_datetime(data["endTime"])
    data = data.sort_values("endTime")

    top_k = data[song_id_key].value_counts().head(k_top).index

    df_top = data[data[song_id_key].isin(top_k)].copy()
    # (song → next_song)
    df_top.loc[:, "next_song"] = df_top[song_id_key].shift(-1)

    df_edges = df_top[df_top["next_song"].isin(top_k)][[song_id_key, "next_song"]]

    transition_counts = (
        df_edges.groupby([song_id_key, "next_song"]).size().reset_index(name="weight")
    )

    # create graph
    G = nx.DiGraph()

    for _, row in transition_counts.iterrows():
        G.add_edge(row[song_id_key], row["next_song"], weight=row["weight"])

    # Create a unique color per node
    nodes = list(G.nodes())
    num_nodes = len(nodes)

    colors = plt.cm.tab10(np.linspace(0, 1, num_nodes))  # hasta 20 colores
    color_map = dict(zip(nodes, colors))

    # List colors in the same order that the nodes in the graph
    node_colors = [color_map[n] for n in nodes]

    # plot graph
    px_h, px_w = img_size
    dpi = 100
    fig = plt.figure(figsize=(px_w / dpi, px_h / dpi), facecolor="black")

    pos = nx.spring_layout(G, k=1.1, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=10_000,
        font_size=14,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=12,
        edge_color="white",
        font_color="white",
    )

    # ---- edge labels (weight) ----
    edge_labels = nx.get_edge_attributes(G, "weight")

    ax = plt.gca()

    # Get Y limits (usually from 0 to 1 or -1 to 1)
    y_min, y_max = ax.get_ylim()
    # move a bit the graph from the top
    ax.set_ylim(y_min, y_max * 1.2)

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=12,
    )

    fig.suptitle(
        title,
        fontsize=28,
        color=GREEN_BLUE_HEXA_COLOR,
        weight="bold",
        y=0.93,  # keep top margin
    )

    plt.savefig(save_path, dpi=300, facecolor="black")
