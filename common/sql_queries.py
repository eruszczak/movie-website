from django.db import connection

get_count_of_current_rates = """
    SELECT COUNT("rate") as "the_count", "rate" FROM (
        SELECT DISTINCT
        (
        SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "rate",

        "movie_title"."id", "movie_title"."name"
        FROM "movie_title"

        JOIN "movie_rating" rating ON ("movie_title"."id" = rating."title_id" AND rating."user_id" = %s)
    ) as "ratings"
    GROUP BY "rate"
    ORDER BY "rate"
"""


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def rating_distribution(user_id):
    with connection.cursor() as cursor:
        cursor.execute(get_count_of_current_rates, [user_id] * 2)
        return dictfetchall(cursor)
