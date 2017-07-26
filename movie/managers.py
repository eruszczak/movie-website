from django.db.models.query import QuerySet


class TitleQuerySet(QuerySet):

    def with_actor_and_title_excluded(self, actor, title):
        """
        :param actor: titles in which that Actor starred
        :param title: title that should be excluded (title details shows the cast and their other movies,
        and I want to exclude from that lists current title)
        :return:
        """
        return self.filter(actor=actor).exclude(const=title.const).order_by('-votes')

    def with_actor_and_title_excluded_and_curr_rating(self, actor, title, user):
        """
        :param user: annotates to each title current rating of this user
        :return:
        """
        return self.with_actor_and_title_excluded(actor, title).extra(select={
                'user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1"""
            }, select_params=[user.id]).order_by('-votes')
