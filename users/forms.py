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
        # fields = ('user.email', 'user.password', 'new_password', 'new_password_confirm', 'imdb_id', 'csv_ratings', 'picture')
        fields = ('imdb_id', 'csv_ratings', 'picture')

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        print(picture, type(picture))
        if isinstance(picture, InMemoryUploadedFile):
            w, h = get_image_dimensions(picture)
            if (w > 200 or h > 200) or (w < 100 or h < 100):
                raise forms.ValidationError("The picture is {}x{} - must be between 100x100px and 200x200px".format(w, h))
            elif picture._size > 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 1mb )")
            elif w != h:
                raise forms.ValidationError("Width and height must be the same")
        return picture

    def clean_csv_ratings(self):
        csv_ratings = self.cleaned_data.get('csv_ratings')
        if isinstance(csv_ratings, InMemoryUploadedFile):
            if csv_ratings._size > 1024 * 1024 * 2:
                raise forms.ValidationError("file too large ( > 2mb )")

        return csv_ratings


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
