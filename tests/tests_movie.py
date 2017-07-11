from datetime import datetime

from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from movie.models import Title, Rating, Watchlist

from movie.functions import create_or_update_rating


class TitleTestCase(TestCase):
    def setUp(self):
        self.title = Title.objects.create(const='123')
        self.title2 = Title.objects.create(const='123132')
        self.user = User.objects.create(username='nick')
        self.user2 = User.objects.create(username='nick2')

    def test_movie_created(self):
        t = Title.objects.filter(const='123')
        self.assertEqual(t.exists(), True)

    def test_const_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            Title.objects.create(const='123')

    def test_slug_is_correct(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction')
        self.assertEqual(t.slug, 'pulp-fiction')

        t2 = Title.objects.create(const='567', name='Pulp Fiction', year='1999')
        self.assertEqual(t2.slug, 'pulp-fiction-1999')

    def test_slug_must_be_unique_for_titles_with_the_same_title_and_year(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        t2 = Title.objects.create(const='567', name='Pulp Fiction', year='1994')
        self.assertEqual(t.slug + 'i', t2.slug)

    def test_str_representation(self):
        t = Title.objects.create(const='567', name='Pulp Fiction', year='1999')
        self.assertEqual(str(t), '{} {}'.format(t.name, t.year))

    def test_count_and_avg_of_current_title_ratings(self):
        Rating.objects.create(title=self.title, user=self.user, rate=1, rate_date=datetime(2015, 10, 10))
        Rating.objects.create(title=self.title, user=self.user, rate=5, rate_date=datetime(2015, 10, 15))

        Rating.objects.create(title=self.title, user=self.user2, rate=10, rate_date=datetime(2015, 10, 20))
        self.assertEqual(self.title.rate['avg'], (5 + 10) / 2)
        self.assertEqual(self.title.rate['count'], 2)

    def test_title_get_absolute_url(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        url = reverse('title_details', kwargs={'slug': t.slug})
        self.assertEqual(t.get_absolute_url(), url)

    def test_title_can_be_updated(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        self.assertEqual(t.can_be_updated, False)

    def test_title_url_imdb_is_set(self):
        assert 'imdb.com/title/123' in self.title.url_imdb

    def test_user_username_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(username='nick')

    # TODO
    def test_relations(self):
        pass

    def test_rating_uniqueness(self):
        pass

    def test_rating_str_representation(self):
        create_or_update_rating(self.title, self.user, 8)
        r = Rating.objects.get(title=self.title, user=self.user)

        self.assertEqual(str(r), '{} {}'.format(r.title.name, r.rate_date))

    def test_first_returns_current_rating(self):
        Rating.objects.create(title=self.title, user=self.user, rate=1, rate_date=datetime(2015, 10, 10))
        r2 = Rating.objects.create(title=self.title, user=self.user, rate=1, rate_date=datetime(2015, 10, 15))
        current = Rating.objects.filter(user=self.user, title=self.title).first()
        self.assertEqual(current, r2)
        self.assertEqual(current.is_current_rating, True)

    # def test_days_between_next_rating_of_this_title(self):
    #     latest_rating_date = datetime(2015, 10, 15)
    #
    #     r1 = Rating.objects.create(title=self.title, user=self.user, rate=1, rate_date=datetime(2015, 10, 10))
    #     r2 = Rating.objects.create(title=self.title, user=self.user, rate=1, rate_date=datetime(2015, 10, 15))
    #
    #     days_between_today_and_latest_rating = (datetime.now() - r2.rate_date).days
    #     self.assertEqual(r1.next_rating_days_diff, 5)
    #     self.assertEqual(r2.next_rating_days_diff, days_between_today_and_latest_rating)


    # def test_rating_without_date_provided_is_from_today(self):
    #     r = Rating.objects.create(title=self.title, user=self.user)
    #     self.assertEqual(r.rate_date, datetime.today())

    def test_rated_title_must_be_deleted_from_watchlist(self):
        earlier = timezone.make_aware(datetime(2015, 10, 15), timezone.get_current_timezone())
        later = timezone.make_aware(datetime(2015, 10, 20), timezone.get_current_timezone())

        Watchlist.objects.create(user=self.user, title=self.title, added_date=earlier)
        self.assertEqual(Watchlist.objects.filter(user=self.user, title=self.title, added_date=earlier).exists(), True)
        Rating.objects.create(title=self.title, user=self.user, rate=8, rate_date=later)
        self.assertEqual(Watchlist.objects.filter(user=self.user, title=self.title, added_date=earlier).exists(), False)

    def test_favourite_titles_ordering(self):
        pass