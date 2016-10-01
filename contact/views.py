from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from .forms import ContactForm
from utils.utils import send_email
from django.contrib import messages


def contact(request):
    form = ContactForm(initial={'nick': request.user.username})

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get('message')
            nick = form.cleaned_data.get('nick')
            subject = form.cleaned_data.get('subject')
            send_email(message='{}. Send by: {}'.format(message, nick), subject=subject)
            messages.success(request, 'email has been sent')
            return redirect(reverse('contact'))
        # messages.error(request, 'there was an error')
    context = {
        'form': form,
        'title': 'contact',
    }
    return render(request, 'contact.html', context)