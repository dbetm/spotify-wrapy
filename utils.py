import json
import os
from typing import Optional

import pandas as pd

from constants import DEFAULT_DATA_DIR



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


if __name__ == '__main__':
    data = load_streaming_history_data()
    print(data.head())
    print("*"*42)
    print(data.describe())
