from wrapy.lang.locale import Locale


class EsLocale(Locale):
    def __init__(self):
        self._total_play = "Total de reproducciones"
        self._song_skips = "Canciones saltadas"
        self._avg_plays_per_day = "Reproducciones promedio por día"
        self._total_play_listened = "Tiempo total escuchado"
        self._month = "Mes"
        self._day = "Día"
        self._hour = "Hora"
        self._minute = "Minuto"
        self._different_artists_listened = "Artistas diferentes escuchados"
        self._different_songs_listened = "Canciones diferentes escuchadas"
        self._time_period = "Periodo de tiempo"
        self._plays_per_weekday_plot_title = "Reproducciones por día de la semana"
        self._plays_per_hour_plot_title = "Reproducciones por hora"
        self._plays_per_month_plot_title = "Reproducciones por mes"
        self._top_songs_card_title = "Canciones más escuchadas"
