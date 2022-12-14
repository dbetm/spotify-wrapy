import pandas as pd

from constants import (
    TOTAL_SECONDS_PER_DAY,
    TOTAL_SECONDS_PER_HOUR,
    TOTAL_SECONDS_PER_MINUTE,
)


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