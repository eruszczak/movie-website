from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile
import re


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')
        # fields = ('username', 'password', 'email')


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('imdb_id', 'csv_ratings', 'picture')

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        print(picture, type(picture))
        if isinstance(picture, InMemoryUploadedFile):
            w, h = get_image_dimensions(picture)
            if (w > 200 or h > 200) or (w < 100 or h < 100):
                raise forms.ValidationError("The picture is {}x{}. Size allowed 100x100px - 200x200px".format(w, h))
            elif picture._size > 1024 * 150:
                raise forms.ValidationError("Image file too large ( > 150kB )")
            elif w != h:
                raise forms.ValidationError("Width and height must be the same")
        return picture

    def clean_csv_ratings(self):
        csv_ratings = self.cleaned_data.get('csv_ratings')
        if isinstance(csv_ratings, InMemoryUploadedFile):
            if csv_ratings._size > 1024 * 1024 * 2:
                raise forms.ValidationError("File too large ( > 2mb )")

        return csv_ratings

    def clean_imdb_id(self):
        imdbid = self.cleaned_data.get('imdb_id')
        valid_id = re.match('ur\d+', imdbid)
        valid_id = valid_id.group() if valid_id else ''
        if not valid_id.startswith('ur') or len(valid_id) < 6:
            raise forms.ValidationError('IMDb ID must start with "ur" and has at least 6 characters')
        return valid_id


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
