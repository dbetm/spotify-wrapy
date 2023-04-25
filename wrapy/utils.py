import json
import os
from datetime import date, datetime
from typing import Any, List, Optional, Tuple

import pandas as pd

from wrapy.constants import DEFAULT_DATA_DIR, LIMIT_DATE_FORMAT


def load_streaming_history_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """Load a user's streaming history Spotify data from a specified file or
    the default directory and returns it as a pandas DataFrame.

    Args:
        file_path (Optional[str], default=None): The path of the JSON file containing the
        streaming history data. If not provided, the function will attempt to load the
        data from a file in the default data directory.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the streaming history data.
    """
    if not file_path:
        files_ = os.listdir(DEFAULT_DATA_DIR)
        file_paths = []

        for file_ in files_:
            if file_.startswith("StreamingHistory"):
                file_paths.append(f"{DEFAULT_DATA_DIR}/{file_}")

        if len(file_paths) == 0:
            raise Exception(
                f"Error trying to find streaming data in default dir ({DEFAULT_DATA_DIR})"
            )

    data = list()
    for file_path in file_paths:
        with open(file_path) as json_file:
            data += json.load(json_file)

    return pd.DataFrame.from_dict(data)


def map_int_day_to_weekday_name(days_week_map: dict, day_id: int) -> str:
    """Given the `day_id` as a numeric integer used by Python to define weekdays (0 is
    Monday and 6 is Sunday), returns the corresponding string name of the weekday."""
    return days_week_map[day_id]


def convert_column_utc_datetime_to_local_time(
    data: pd.DataFrame,
    new_tz: str,
    column_name: str,
    new_column_name: str,
    date_format: str = "%Y-%m-%d %H:%M",
) -> pd.DataFrame:
    """Converts a pandas DataFrame column with datetime values in UTC to a specified
    local time zone, creating a new column with the converted values.

    Args:
        - data (pd.DataFrame): The input pandas DataFrame containing the datetime column
        to be converted.
        - new_tz (str): The target timezone to convert the datetime values to,
        e.g., 'US/Pacific'.
        - column_name (str): The name of the existing column containing the datetime
        values in UTC.
        - new_column_name (str): The name of the new column that will store the
        datetime values in the target timezone.
        - date_format (str, optional): The format of the datetime values in the
        input column. Defaults to `%Y-%m-%d %H:%M`.

    Returns:
        pd.DataFrame: The modified DataFrame with the new column containing datetime values in the target timezone.
    """
    data[column_name] = pd.to_datetime(data[column_name], format=date_format, utc=True)

    data[new_column_name] = data[column_name].dt.tz_convert(tz=new_tz)

    return data


def separate_di_tuples_in_two_lists(tuples: List[Tuple[Any, Any]]) -> Tuple[list, list]:
    """Separates a list of 2-tuples into two separate lists, with the first
    elements in one list and the second elements in the other list.
    """
    x, y = zip(*tuples)

    return list(x), list(y)


def write_text_lines_in_new_text_file(strings: List[str], filepath: str):
    """Given a list of strings and a filepath. It will write each string in a new line.
    as plain text."""
    # open a file in write mode
    with open(filepath, "w") as f:
        # write all the strings to the file at once
        f.writelines(string + "\n\n" for string in strings)


def parse_str_to_date(date_str: str) -> date:
    """Create a Python date object from a string in the format `%Y-%m-%d`."""
    return datetime.strptime(date_str, LIMIT_DATE_FORMAT).date()


def filter_data_by_dates(
    data: pd.DataFrame, column_name: str, start_date: date, end_date: date
) -> pd.DataFrame:
    """Filter data by the column_name given and the start_date and end_date"""
    timezone_name = data[column_name].dt.tz
    assert data[column_name].dtype == pd.core.dtypes.dtypes.DatetimeTZDtype(
        tz=timezone_name
    )

    start_date = pd.Timestamp(ts_input=start_date, tz=timezone_name)
    end_date = pd.Timestamp(ts_input=end_date, tz=timezone_name)

    return data[(data[column_name] >= start_date) & (data[column_name] <= end_date)]
