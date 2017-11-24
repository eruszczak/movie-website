[![Python Version](https://img.shields.io/badge/python-3.6-brightgreen.svg)](https://python.org) [![Django Version](https://img.shields.io/badge/django-1.11-brightgreen.svg)](https://djangoproject.com)

# Why
Created for helping me with tracking watched movies/tv-shows.
It is helpful because if you rate again some title on IMDb, information about previous rating is overwritten.

# How it works
* IMDb provides XML for getting last 250 titles in your ratings/watchlist and also allows exporting your full ratings
* you can upload this exported file into your settings and then update your ratings on this site
* if your IMDb's lists are public you can provide your IMDb ID and your ratings/watchlist will be kept up-to-date
* you can still use this site without having IMDb account but you won't be able to add new titles (they are added only when needed - while updating user's ratings, watchlist or recommending titles to a user)

# Todo
* redo layout
* add tests
* use TMDb as data source
