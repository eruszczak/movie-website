#### This is a new version of a Django website from [this repo](https://github.com/kierrez/website/blob/master/README.md) that I'm currently working on.

Created for helping with tracking watched movies/tv-shows.

It is helpful because if you rate again some title on IMDb, information about previous rating is overwritten.


This version's features:
- creating accounts
- uploading ratings.csv file exported from IMDb and then using it for importing your ratings to the website
- if you provide your imdb accounts' id and you have a public profile your ratings will be kept up-to-date
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