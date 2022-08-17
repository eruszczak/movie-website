import os
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile

from shared.forms import SizeExtValidatorMixin
from shared.widgets import MyClearableFileInput

User = get_user_model()


class RegisterForm(UserCreationForm):
    login_after = forms.BooleanField(initial=True, label='Log me in after', required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'login_after')


class UserUpdateForm(SizeExtValidatorMixin, forms.ModelForm):

    def __init__(self, original_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_instance = original_instance
        self.fields['imdb_id'].widget.attrs.update({'placeholder': 'ur12346789'})

    class Meta:
        model = User
        fields = ('tagline', 'imdb_id')
        help_texts = {
            'imdb_id': 'If you will provide your IMDb Id and your lists are public, '
                       'you will be able to update your ratings/watchlist on your profile page.'
        }

    def clean_imdb_id(self):
        imdb_id = self.cleaned_data.get('imdb_id')
        if imdb_id:
            valid_id = re.match('ur\d+', imdb_id)
            valid_id = valid_id.group() if valid_id else ''
            if not valid_id.startswith('ur') or len(valid_id) < 6:
                raise forms.ValidationError('IMDb ID must start with "ur" and have at least 6 characters')
            return valid_id
        return imdb_id

    def save(self, commit=True):
        self.remove_not_used_files()
        super().save(commit)

    def remove_not_used_files(self):
        """if any file field has changed and it had file before update, remove that file"""
        file_fields_to_clean = ['csv_ratings']
        for field in file_fields_to_clean:
            if field in self.changed_data:
                original_field = getattr(self.original_instance, field)
                if original_field:
                    os.remove(original_field.path)
