from wrapy.lang.locale import Locale


class EnLocale(Locale):
    def __init__(self):
        self._total_play = "Total plays"
        self._song_skips = "Skipped songs"
        self._avg_plays_per_day = "Average plays per day"
        self._total_play_listened = "Total time listened"
        self._month = "Month"
        self._day = "Day"
        self._hour = "Hour"
        self._minute = "Minutes"
        self._different_artists_listened = "Different artists listened"
        self._different_songs_listened = "Different songs listened"
        self._time_period = "Time period"
        self._plays_per_weekday_plot_title = "Plays per weekday"
        self._plays_per_hour_plot_title = "Plays per hour"
        self._plays_per_month_plot_title = "Plays per month"
        self._top_songs_card_title = "Top songs listened to"
