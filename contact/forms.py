from django import forms


class ContactForm(forms.Form):
    nick = forms.CharField(max_length=50)
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "what's your problem?", 'rows': 5}),
                              max_length=500)