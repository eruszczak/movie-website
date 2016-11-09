from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from common.utils import send_email
from .forms import ContactForm


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
        # messages.warning(request, 'there was an error')
    context = {
        'form': form,
        'title': 'contact',
    }
    return render(request, 'contact.html', context)