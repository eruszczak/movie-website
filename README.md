# My first Django website
#### temporary hosting: http://kierrez.pythonanywhere.com
Created for helping me with tracking watched movies/tv-shows.

It is helpful because:
- if you rate again some title on IMDb, information about previous rating date and your rating is overwritten
- can see what titles I have seen in given month /2016/9/
- can see what titles I have seen directed by given person /director/2/ 
- users can recommend me titles by inserting IMDb's link /recommend/
- can mark titles as "want to see again" and then can see how long it took /watchlist/ 
- also I keep up-to-date my IMDb's Watchlist so I know which titles should be deleted from it /watch/
- have some cool charts /charts/

How the process looks like:
- I exported my IMDb ratings to .csv file
- then used it to populate my database (done by [this function](https://github.com/kierrez/website/blob/master/prepareDB.py#L73))
- at this point I have all my ratings but need a way to update them daily (done by [this function](https://github.com/kierrez/website/blob/master/prepareDB.py#L87) which uses [IMDb's RSS](http://rss.imdb.com/user/ur44264813/ratings))



for getting details about title [OMDb API](http://www.omdbapi.com/)

## Plans
- [ ] Send email with titles which should be deleted from IMDb Watchlist
- [ ] Host it on my own VPS
- [ ] Custom domain name
- [ ] Use PostgreSQL instead of SQLite
- [ ] Allow other users to use it for their IMDb account
