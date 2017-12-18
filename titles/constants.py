DIRECTOR = 0
DIRECTOR_DISPLAY = 'Director'

SCREENPLAY = 1
SCREENPLAY_DISPLAY = 'Screenplay'

CREATOR = 2
CREATOR_DISPLAY = 'Creator'

TITLE_CREW_JOB = {
    DIRECTOR_DISPLAY: DIRECTOR,
    SCREENPLAY_DISPLAY: SCREENPLAY,
    CREATOR_DISPLAY: CREATOR
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

IMAGE_SIZES = {
    'backdrop_user': 'w1920_and_h318_bestv2',
    'backdrop_title': 'w1280',
    'small': 'w185_and_h278_bestv2',
    'card': 'w500_and_h281_bestv2',
    'small_person': 'w185_and_h278_bestv2'
}
