from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse

from movie.models import Title


class TitleTestCase(TestCase):
    def setUp(self):
        Title.objects.create(const='123')

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
        pass
        # t = Title.objects.create(const='567', name='Pulp Fiction', year='1999')
        # self.assertEqual(t.__str__, '{} {}'.format(t.name, t.year))

    def test_const_must_be_valid(self):
        pass

    def test_avg_of_current_ratings(self):
        pass

    def test_title_get_absolute_url(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        url = reverse('title_details', kwargs={'slug': t.slug})
        self.assertEqual(t.get_absolute_url(), url)

    def test_title_can_be_updated(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        self.assertEqual(t.can_be_updated, False)

    def test_title_url_imdb_is_set(self):
        t = Title.objects.create(const='1234', name='Pulp Fiction', year='1994')
        assert 'imdb.com/title/1234' in t.url_imdb
