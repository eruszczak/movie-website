DIRECTOR = 0
DIRECTOR_DISPLAY = 'Director'

SCREENPLAY = 1
SCREENPLAY_DISPLAY = 'Screenplay'

TITLE_CREW_JOB = {
    DIRECTOR_DISPLAY: DIRECTOR,
    SCREENPLAY_DISPLAY: SCREENPLAY
}

TITLE_CREW_JOB_CHOICES = ((value, display) for display, value in TITLE_CREW_JOB.items())

MOVIE = 0
MOVIE_DISPLAY = 'Movie'

SERIES = 1
SERIES_DISPLAY = 'TV Shows'

TITLE_TYPE_CHOICES = (
    (MOVIE, MOVIE_DISPLAY),
    (SERIES, SERIES_DISPLAY)
)


# matches my title model attribute names with tmdb's names
TITLE_MODEL_MAP = {
    'tmdb_id': 'id',
    # 'imdb_id': 'imdb_id',
    'overview': 'overview',
    'release_date': 'release_date',
    'runtime': 'runtime',
    'name': 'title',
    'poster_path': 'poster_path'
}