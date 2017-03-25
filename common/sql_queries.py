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

avg_of_current_user_ratings = """
    SELECT AVG("current_rating") as "avg", COUNT("current_rating") as "count" FROM (
        SELECT DISTINCT
        (SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "current_rating",

        "movie_title"."id"
        FROM "auth_user"

        JOIN "movie_rating" ON ("movie_rating"."user_id" = "auth_user"."id")
        JOIN "movie_title" ON ("movie_title"."id" = "movie_rating"."title_id")
        WHERE "auth_user"."id" = %s
    ) as "forEveryTitleCurrentRating"
"""

avg_of_current_ratings_of_title = """
    SELECT AVG("current_rating"), COUNT("current_rating") FROM (
        SELECT DISTINCT
        (SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = "auth_user"."id"
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "current_rating",

        "movie_title"."id", "auth_user"."id"
        FROM "auth_user"

        JOIN "movie_rating" ON ("movie_rating"."user_id" = "auth_user"."id")
        JOIN "movie_title" ON ("movie_title"."id" = "movie_rating"."title_id")
        WHERE "movie_title"."id" = %s
    ) as "currentRatingsOfTitle"
"""

avg_for_2_user_of_only_common_curr_ratings = """
    SELECT AVG("current_rating_user1") as "avg_user", AVG("current_rating_user2") as "avg_req_user", COUNT(*) FROM (
        SELECT DISTINCT
        (
        SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "current_rating_user1",

        (
        SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "current_rating_user2",

        "movie_title"."id"
        FROM "movie_title"

        --need to twice join the same table so in the where condition I can check for 2 ids
        JOIN "movie_rating" ON ("movie_title"."id" = "movie_rating"."title_id")
        JOIN "movie_rating" rating ON ("movie_title"."id" = rating."title_id")
        WHERE ("movie_rating"."user_id" = %s AND rating."user_id" = %s)
    ) as "forEveryTitleRatingFor2Users"
"""

rated_higher_or_lower_sorted_by_rate_diff = """
    SELECT {} as "rate_diff", * FROM (
        SELECT DISTINCT
        (
        SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "user_rate",

        (
        SELECT rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id
        AND rating.user_id = %s
        ORDER BY rating.rate_date DESC LIMIT 1
        ) AS "req_user_rate",

        "movie_title".const, "movie_title".name, "movie_title".img_thumbnail, "movie_title".img
        FROM "movie_title"

        --need to twice join the same table so in the where condition I can check for 2 ids
        JOIN "movie_rating" rating1 ON ("movie_title"."id" = rating1."title_id")
        JOIN "movie_rating" rating2 ON ("movie_title"."id" = rating2."title_id")
        WHERE (rating1."user_id" = %s AND rating2."user_id" = %s)
    ) as "titlesThaAreRatedByBothUsersAndShowTheirCurrentRatings"
    WHERE "user_rate" {} "req_user_rate"
    ORDER BY rate_diff DESC
    LIMIT {}
"""

# todo this can be done in similar way as I fixed getting archived watchlist
curr_rate_of_followed_user_for_title = """
    SELECT
    (SELECT rate
    FROM movie_rating as rating
    WHERE rating.user_id = "DistinctTitlesRatedByFollowed".user_followed_id
    AND rating.title_id = "DistinctTitlesRatedByFollowed"."title_id"
    ORDER BY rating.rate_date DESC LIMIT 1
    ) AS "followed_curr_rating",
    * FROM (
    SELECT DISTINCT
    "movie_rating"."title_id", "users_userfollow"."user_follower_id", "users_userfollow"."user_followed_id",
    T3.username, T5.picture
    FROM "users_userfollow"
    INNER JOIN "auth_user" T3 ON ("users_userfollow"."user_followed_id" = T3."id")
    INNER JOIN "movie_rating" ON (T3."id" = "movie_rating"."user_id")
    INNER JOIN "users_userprofile" T5 ON (T3."id" = T5."id")
    WHERE ("users_userfollow"."user_follower_id" = %s AND "movie_rating"."title_id" = %s)
    ) AS "DistinctTitlesRatedByFollowed"
"""

select_current_rating = """
    SELECT rate FROM movie_rating as rating
    WHERE rating.title_id = movie_title.id
    AND rating.user_id = %s
    ORDER BY rating.rate_date DESC LIMIT 1
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


def avg_of_user_current_ratings(user_id):
    with connection.cursor() as cursor:
        cursor.execute(avg_of_current_user_ratings, [user_id] * 2)
        return dictfetchall(cursor)[0]


# todo this is almost done. i just have to get distinct('user')
def avg_of_title_current_ratings(title_id):
    with connection.cursor() as cursor:
        cursor.execute(avg_of_current_ratings_of_title, [title_id])
        return dictfetchall(cursor)[0]


# todo similar as upper. just need to make 2 queries to get avgs but filter common ratings first
def avgs_of_2_users_common_curr_ratings(user_id, req_user):
    with connection.cursor() as cursor:
        cursor.execute(avg_for_2_user_of_only_common_curr_ratings, [user_id, req_user, req_user, user_id])
        return dictfetchall(cursor)[0]

# todo
def titles_rated_higher_or_lower(user_id, req_user, sign, limit):
    """

    """
    with connection.cursor() as cursor:
        rate_diff_col_operation = '-' if sign == '<' else '+'
        q = '"req_user_rate" + "user_rate"' if rate_diff_col_operation == '-' else '"user_rate" - "req_user_rate"'
        cursor.execute(rated_higher_or_lower_sorted_by_rate_diff.format(
            q, sign, limit), [user_id, req_user, req_user, user_id])
        return dictfetchall(cursor)


def curr_title_rating_of_followed(follower_id, title_id):
    with connection.cursor() as cursor:
        cursor.execute(curr_rate_of_followed_user_for_title, [follower_id, title_id])
        return dictfetchall(cursor)