import re
import os

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    login_after = forms.BooleanField(initial=True, label='Log me in after', required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'login_after')


class UserUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imdb_id'].widget.attrs.update({'placeholder': 'eg. ur12346789'})

    class Meta:
        model = User
        fields = ('picture', 'tagline', 'imdb_id', 'csv_ratings')
        labels = {
            'picture': 'Avatar',
            'csv_ratings': 'Imdb ratings (csv)'
        }
        help_texts = {
            'imdb_id': 'If you will provide your IMDb Id and your lists are public, '
                       'you will be able to update your ratings/watchlist on your profile page.',
            'csv_ratings': 'If you want to import your existing IMDb ratings, '
                           'go to your IMDb Ratings List and at the bottom of the page you can export it, '
                           'then upload it here and you will be able to update your ratings '
                           'on your profile page.'
        }

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if isinstance(picture, UploadedFile):
            w, h = get_image_dimensions(picture)
            name, ext = os.path.splitext(str(picture))
            if ext not in ('.png', '.jpg'):
                raise forms.ValidationError('Allowed file extensions: jpg, png.')

            self.validate_size(picture.size, 1024 * 150)

            min_width, max_width = 100, 200
            valid_dimensions_conditions = [min_width <= h <= max_width, min_width <= w <= max_width, w == h]
            if not all(valid_dimensions_conditions):
                raise forms.ValidationError(
                    f'The image is {w}x{h}px. '
                    f'It must be a square with width between {min_width}px and {max_width}px.'
                )

            return picture
        return None

    def clean_csv_ratings(self):
        csv_ratings = self.cleaned_data.get('csv_ratings')
        if isinstance(csv_ratings, UploadedFile):
            self.validate_size(csv_ratings.size, 1024 * 1024 * 2)
            return csv_ratings
        return None

    def clean_imdb_id(self):
        imdb_id = self.cleaned_data.get('imdb_id')
        if imdb_id:
            valid_id = re.match('ur\d+', imdb_id)
            valid_id = valid_id.group() if valid_id else ''
            if not valid_id.startswith('ur') or len(valid_id) < 6:
                raise forms.ValidationError('IMDb ID must start with "ur" and have at least 6 characters')
            return valid_id
        return None

    @staticmethod
    def validate_size(file_size, max_size):
        """raises ValidationError if file_size is bigger than max_size (in kB)"""
        if file_size > max_size:
            raise forms.ValidationError(
                f'Maximum file size is {int(max_size / 1024)} kB. Uploaded file\'s size is {int(file_size / 1024)} kB'
            )
