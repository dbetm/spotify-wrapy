import json
import os
from typing import Any, List, Optional, Tuple

import pandas as pd

from constants import DAYS_WEEK_MAP, DEFAULT_DATA_DIR


def load_streaming_history_data(file_path: Optional[str] = None) -> pd.DataFrame:
    if not file_path:
        files_ = os.listdir(DEFAULT_DATA_DIR)

        try:
            file_path = list(
                filter(lambda a: "StreamingHistory" in a, files_)
            )[0]
            file_path = f"{DEFAULT_DATA_DIR}/{file_path}"
        except Exception as e:
            raise e(
                f"Error trying to find streaming data in default dir ({DEFAULT_DATA_DIR})"
            )
    
    with open(file_path) as json_file:
        data = json.load(json_file)

    return pd.DataFrame.from_dict(data)


def map_int_day_to_weekday_name(day_id: int) -> str:
    return DAYS_WEEK_MAP[day_id]


def convert_column_utc_datetime_to_local_time(
    data: pd.DataFrame,
    new_tz: str,
    column_name: str,
    date_format: str = "%Y-%m-%d %H:%M",
) -> pd.DataFrame:
    data[column_name] =  pd.to_datetime(
        data[column_name], format=date_format, utc=True
    )

    data[column_name] = data[column_name].dt.tz_convert(tz=new_tz)

    return data


def separate_di_tuples_in_two_lists(tuples: List[Tuple[Any, Any]]) -> Tuple[list, list]:
    x = list()
    y = list()

    for x_i, y_i in tuples:
        x.append(x_i)
        y.append(y_i)

    return x, y


def write_text_lines_in_new_text_file(strings: List[str], filepath: str):
    # open a file in write mode
    with open(filepath, "w") as f:
        # write all the strings to the file at once
        f.writelines(string + '\n\n' for string in strings)
