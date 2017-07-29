import re
import os

from django import forms
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


# class


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('imdb_id', 'csv_ratings', 'picture')

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if isinstance(picture, InMemoryUploadedFile):
            w, h = get_image_dimensions(picture)
            name, ext = os.path.splitext(str(picture))
            if ext not in ('.png', '.jpg'):
                raise forms.ValidationError('Avatar must be either .jpg or .png')
            if (w > 200 or h > 200) or (w < 100 or h < 100):
                raise forms.ValidationError('The picture is {}x{}. Size allowed 100x100px - 200x200px'.format(w, h))
            elif picture.size > 1024 * 150:
                raise forms.ValidationError('Image file too large (>150kB)')
            elif w != h:
                raise forms.ValidationError('Width and height must be the same')
        return picture

    def clean_csv_ratings(self):
        csv_ratings = self.cleaned_data.get('csv_ratings')
        if isinstance(csv_ratings, InMemoryUploadedFile):
            if csv_ratings.size > 1024 * 1024 * 2:
                raise forms.ValidationError('File too large ( > 2MB )')
        return csv_ratings

    def clean_imdb_id(self):
        imdb_id = self.cleaned_data.get('imdb_id')
        if not imdb_id:
            raise forms.ValidationError('IMDb ID is missing')

        valid_id = re.match('ur\d+', imdb_id)
        valid_id = valid_id.group() if valid_id else ''
        if not valid_id.startswith('ur') or len(valid_id) < 6:
            raise forms.ValidationError('IMDb ID must start with "ur" and have at least 6 characters')
        return valid_id
