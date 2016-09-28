# My first Django website
#### temporary hosting: http://kierrez.pythonanywhere.com
Created for helping me with tracking watched movies/tv-shows.

It is helpful because:
- if you rate again some title on IMDb, information about previous rating is overwritten
- through the title detail page I can see quickly:
  - what titles I have seen with the same rating /rated/7/
  - what titles I have seen with its genres /genre/drama/
  - what titles I have seen in that month /2016/9/
  - what titles I have seen directed by the same director /director/2/
  - previous ratings!
- people can /recommend/ me titles by inserting IMDb's link and when I watch something from the list it is shown
- can mark titles as "want to see again" and then can see how long it took me to do it /watchlist/
- also I keep up-to-date my IMDb's Watchlist so I know which titles should be deleted from it /watchlist-imdb/
- initially I wanted to build an API for javascript /charts/, ended up using it for a [GitHub Page](http://kierrez.github.io/) and dynamic /search/ing too
- can change rating without changing rating date /title/heat-1995/edit/

How the process looks like:
- I exported my IMDb ratings to .csv file
- then used it to populate my database (done by [this function](https://github.com/kierrez/website/blob/master/prepareDB.py#L73))
- at this point I have all my ratings but need a way to update them daily (done by [this function](https://github.com/kierrez/website/blob/master/prepareDB.py#L87) which uses [IMDb's RSS](http://rss.imdb.com/user/ur44264813/ratings))



for getting details about title [OMDb API](http://www.omdbapi.com/)

## Plans
- [ ] Host it on my own VPS
- [ ] Custom domain name
- [ ] Use PostgreSQL instead of SQLite
- [ ] Allow other users to use it for their IMDb account

## Problems
- [ ] Free pythonanywhere account doesn't allow to download stuff (so new titles don't have a posters)
- [ ] API doesn't provide complete info about seasons and episodes, which is why I don't want to use it at all