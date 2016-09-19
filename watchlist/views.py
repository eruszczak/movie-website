from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

def index(request):
    return render(request, 'watchlist/index.html')