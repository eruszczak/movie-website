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

titles_rated_by_user_with_current_rating_equals = """
    SELECT	*,
        CASE WHEN EXISTS (
        SELECT 1 FROM "movie_rating" rating
            WHERE rating."user_id" = %s
            AND "titlesWithCurrentRating"."id" = rating."title_id"
        ) THEN 1 ELSE 0 END
        AS "seen_by_user",

        CASE WHEN EXISTS (
        SELECT 1 FROM "movie_watchlist" watchlist
            WHERE watchlist."user_id" = %s
            AND "titlesWithCurrentRating"."id" = watchlist."title_id"
            AND watchlist."deleted" IS FALSE
        ) THEN 1 ELSE 0 END
        AS "has_in_watchlist",

        CASE WHEN EXISTS (
        SELECT 1 FROM "movie_favourite" favourite
            WHERE favourite."user_id" = %s
            AND "titlesWithCurrentRating"."id" = favourite."title_id"
        ) THEN 1 ELSE 0 END
        AS "has_in_favourites"
    FROM (
        SELECT DISTINCT (
            SELECT rate FROM movie_rating as rating
            WHERE rating.title_id = movie_title.id
            AND rating.user_id = %s
            ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "curr_rating",

        "movie_title".* FROM "movie_title"

        JOIN "movie_rating" rating ON ("movie_title"."id" = rating."title_id" AND rating."user_id" = %s)
    ) as "titlesWithCurrentRating"
    WHERE "curr_rating" = %s
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


def titles_user_saw_with_current_rating(user_id, rating, req_user):
    with connection.cursor() as cursor:
        # cursor.execute(titles_rated_by_user_with_current_rating_equals, [user_id, user_id, rating])
        cursor.execute(titles_rated_by_user_with_current_rating_equals, [req_user] * 3 + [user_id] * 2 + [rating])
        return dictfetchall(cursor)
