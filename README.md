#### This is a new version of a Django website from [this repo](https://github.com/kierrez/website/blob/master/README.md) that I'm currently working on.
Doing this project I realised that DRY principle is very important and that writing tests is worth it.

Created for helping me with tracking watched movies/tv-shows.
It is helpful because if you rate again some title on IMDb, information about previous rating is overwritten.

* IMDb provides XML for getting last 250 titles in your ratings/watchlist and also allows export your full ratings
* you can upload this exported file into your settings and then update your ratings on this site
* also, if your IMDb's lists are public you can provide your IMDb ID and your ratings/watchlist will be kept up-to-date
* and I am using [OMDb API](http://www.omdbapi.com/) for getting data about those titles 
* you can still use this site without having IMDb account but you won't be able to add new titles (they are added only when needed - while updating user's ratings, watchlist or recommending titles to a user)

This version's features:
- you can follow other users and then easily recommend them titles (you can also see how long it took them to watch it)
- migrated from SQLite to PostgreSQL
- watchlist
  - easy to update, just like ratings
  - you can add titles to watchlist on IMDb or on the website
  - you can see what titles have been already watched and should be deleted from the list
- the database with titles is updated when:
  - missing titles will be added if someone updates his ratings (using csv file or auto-updater)
  - user adds it using a form (only IMDb id/link is needed)
  - someone wants to recommend some title to somebody and it's not already added
- more searching options
- got rid of redundant templates and views


# Todo
* finish refactoring
* add tests