import json
import os
from typing import Optional

import pandas as pd

from constants import DAYS_WEEK_MAP, DEFAULT_DATA_DIR



def load_streaming_history_data(file_path: Optional[str] = None) -> pd.DataFrame:
    if not file_path:
        files_ = os.listdir(DEFAULT_DATA_DIR)

        try:
            file_path = list(
                filter(lambda a: "StreamingHistory" in a, files_)
            )[0]
            file_path = f"{DEFAULT_DATA_DIR}{file_path}"
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


if __name__ == '__main__':
    data = load_streaming_history_data()
    print(data.head())
    print("*"*42)
    print(data.describe())
