# About
This is a new version of a Django website from [this repo](https://github.com/reryk/website/blob/master/README.md).
On this version I have been working for a few months with breaks. Recently I realized that there is not that much of code but it's because I wrote something once and then found a better way to do it. Overall it was a great learning experience.

# Used tools
* Django 1.10
* Django Rest Framework 3.5
* Django Debug Toolbar
* Django compressor
* Bootstrap
* Jquery

# Why
Created for helping me with tracking watched movies/tv-shows.
It is helpful because if you rate again some title on IMDb, information about previous rating is overwritten.

# How it works
* IMDb provides XML for getting last 250 titles in your ratings/watchlist and also allows exporting your full ratings
* you can upload this exported file into your settings and then update your ratings on this site
* if your IMDb's lists are public you can provide your IMDb ID and your ratings/watchlist will be kept up-to-date
* I am using [OMDb API](http://www.omdbapi.com/) for getting data about titles 
* you can still use this site without having IMDb account but you won't be able to add new titles (they are added only when needed - while updating user's ratings, watchlist or recommending titles to a user)

# Todo
* finish refactoring
* add tests

# Summary
* Doing this project I realised that DRY principle is very important and that writing tests is worth it
* I learned about Django
* I got to know how to deploy it on the VPS
* I learned how HTTP works, what are the roles of nginx and gunicorn
* I learned about common web security vulnerabilities
* I learned how to increase loading speed of the website (caching, gzipping, bundling and minification, optimizing SQL queries)

# This version's features:
* watchlist
  * easy to update, just like ratings
  * you can add titles to watchlist on IMDb or on the website
  * you can see what titles have been already watched and should be deleted from the list
* following other users
You can follow other users and then easily recommend them titles (you can also see how long it took them to watch it)

* flexible way for backuping titles and importing them (example)

## user's profile
* see charts of your ratings
![charts](/static/zscreens/charts.gif)
## searching