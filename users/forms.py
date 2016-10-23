from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


# class RegisterFormUserProfile(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())
#
#     class Meta:
#         model = UserProfile
#         fields = ('username', 'password', 'email')

class EditProfileForm(forms.ModelForm):
    # user.password = forms.CharField(widget=forms.PasswordInput())
    # new_password = forms.CharField(widget=forms.PasswordInput())
    # new_password_confirm = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        # fields = ('user.email', 'user.password', 'new_password', 'new_password_confirm', 'imdb_id', 'imdb_ratings', 'picture')
        fields = ('imdb_id', 'imdb_ratings', 'picture')

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        print(picture, type(picture))
        if isinstance(picture, InMemoryUploadedFile):
            w, h = get_image_dimensions(picture)
            if (w > 200 or h > 200) or (w < 100 or h < 100):
                raise forms.ValidationError("The picture is {}x{}. It's supposed to be between 100x100px and 200x200px".format(w, h))
            if picture._size > 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 1mb )")
        return picture

    def clean_imdb_ratings(self):
        imdb_ratings = self.cleaned_data.get('imdb_ratings')
        if isinstance(imdb_ratings, InMemoryUploadedFile):
            if imdb_ratings._size > 1024 * 1024 * 2:
                raise forms.ValidationError("file too large ( > 2mb )")

        return imdb_ratings


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
