DIRECTOR = 0
DIRECTOR_DISPLAY = 'Director'

SCREENPLAY = 1
SCREENPLAY_DISPLAY = 'Screenplay'

CREATED_BY = 2
CREATED_BY_DISPLAY = 'Creator'

TITLE_CREW_JOB = {
    DIRECTOR_DISPLAY: DIRECTOR,
    SCREENPLAY_DISPLAY: SCREENPLAY,
    CREATED_BY: CREATED_BY_DISPLAY
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
MOVIE_MODEL_MAP = {
    'tmdb_id': 'id',
    # 'imdb_id': 'imdb_id',
    'overview': 'overview',
    'release_date': 'release_date',
    'runtime': 'runtime',
    'name': 'title',
    'poster_path': 'poster_path'
}

# "backdrop_path": "/56v2KjBlU4XaOv9rVYEQypROD7P.jpg", vs poster_path
# created_by - CREW
# seasons
# episodes
SERIES_MODEL_MAP = {
    'release_date': 'first_air_date',
    'name': 'name',
    'tmdb_id': 'id',
}

MODEL_MAP = {
    MOVIE: MOVIE_MODEL_MAP,
    SERIES: SERIES_MODEL_MAP
}
