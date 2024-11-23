#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show  # Import db and models
from flask_migrate import Migrate 

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)  # Bind the db object to the app
migrate = Migrate(app, db)  # Initialize Migrate


# TODO: connect to a local postgresql database - DONE by adding the DB connection line in config.py

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Moved to models.py for Separation of Concers.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # Show recently listed artists and venues
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  return render_template('pages/home.html', artists=recent_artists, venues=recent_venues)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. - DONE
  venues = Venue.query.all()
  data = []
  cities_states = set()
  for venue in venues:
      cities_states.add((venue.city, venue.state))

  cities_states = list(cities_states)
  cities_states.sort(key=lambda x: (x[1], x[0]))

  for loc in cities_states:
      venues_list = []
      for venue in venues:
          if (venue.city == loc[0]) and (venue.state == loc[1]):
              venues_list.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
              })
      data.append({
          "city": loc[0],
          "state": loc[1],
          "venues": venues_list
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" - DONE
  search_term = request.form.get('search_term', '')
  search_terms = search_term.split(",")  # Split the search term by comma
  if len(search_terms) == 2:  # Check if both city and state are provided
      city = search_terms[0].strip()
      state = search_terms[1].strip()
      venues = Venue.query.filter(Venue.city.ilike(f"%{city}%"), Venue.state.ilike(f"%{state}%")).all()
  else:
      venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  response = {
      "count": len(venues),
      "data": []
  }
  for venue in venues:
      response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id - DONE
  venue = Venue.query.get(venue_id)
  if not venue:
      return render_template('errors/404.html'), 404

  past_shows = []
  upcoming_shows = []
  now = datetime.now()
  for show in venue.shows:
      if show.start_time < now:
          past_shows.append({
              "artist_id": show.artist_id,
              "artist_name": show.artist.name,
              "artist_image_link": show.artist.image_link,
              "start_time": str(show.start_time)
          })
      elif show.start_time > now:
          upcoming_shows.append({
              "artist_id": show.artist_id,
              "artist_name": show.artist.name,
              "artist_image_link": show.artist.image_link,
              "start_time": str(show.start_time)
          })
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():  
  # TODO: insert form data as a new Venue record in the db, instead - DONE
  # TODO: modify data to be the data object returned from db insertion - DONE
  error = False
  form = VenueForm(request.form)
  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )
    app.logger.info('Creating venue: %s', venue.name)  # Log venue creation attempt
    db.session.add(venue)
    db.session.commit()
    app.logger.info('Venue created successfully: %s', venue.name)  # Log success
  except:
    app.logger.error('Error creating venue: %s', str(e))  # Log the specific error
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead. - DONE
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. - DONE
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted.')
  else:
    flash('Venue was successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage - DONE in templates/pages/show_artist.html
  return redirect(url_for('index'))  # Redirect to the homepage after deletion

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database - DONE
  artists = Artist.query.all()
  data = []
  for artist in artists:
      data.append({
          "id": artist.id,
          "name": artist.name 
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band". - DONE
  search_term = request.form.get('search_term', '')
  search_terms = search_term.split(",")  # Split the search term by comma
  if len(search_terms) == 2:  # Check if both city and state are provided
      city = search_terms[0].strip()
      state = search_terms[1].strip()
      artists = Artist.query.filter(Artist.city.ilike(f"%{city}%"), Artist.state.ilike(f"%{state}%")).all()
  else:
      artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  response = {
      "count": len(artists),
      "data": []
  }
  for artist in artists:
      response["data"].append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), artist.shows)))
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id - DONE
  artist = Artist.query.get(artist_id)
  if not artist:
      return render_template('errors/404.html'), 404

  past_shows = []
  upcoming_shows = []
  now = datetime.now()
  for show in artist.shows:
      if show.start_time < now:
          past_shows.append({
              "venue_id": show.venue_id,
              "venue_name": show.venue.name,
              "venue_image_link": show.venue.image_link,
              "start_time": str(show.start_time)
          })
      elif show.start_time > now:
          upcoming_shows.append({
              "venue_id": show.venue_id,
              "venue_name": show.venue.name,
              "venue_image_link": show.venue.image_link,
              "start_time": str(show.start_time)
          })

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone, 
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)  # Fetch the artist from the database

  if not artist:
    return render_template('errors/404.html'), 404

  # TODO: populate form with fields from artist with ID <artist_id> - DONE
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes - DONE
  error = False
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  try:
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be updated.')
  else:
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)  # Fetch the venue from the database

  if not venue:
    return render_template('errors/404.html'), 404

  # TODO: populate form with values from venue with ID <venue_id> - DONE
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes - DONE
  error = False
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be updated.')
  else:
    flash('Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead - DONE
  # TODO: modify data to be the data object returned from db insertion - DONE

  error = False
  form = ArtistForm(request.form)
  try:
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead. - DONE
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html') 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. - DONE
  shows = Show.query.all()
  data = []
  for show in shows:
      data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.start_time)
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form - DONE
  # TODO: insert form data as a new Show record in the db, instead - DONE
  error = False
  form = ShowForm(request.form)
  try:
      artist = Artist.query.get(form.artist_id.data)
      venue = Venue.query.get(form.venue_id.data)
      
      # BONUS Task - Check if the show time is within the artist's available times
      show_time = form.start_time.data
      artist_available_times = artist.available_times
      if str(show_time) not in artist_available_times:
          flash('Show time is outside of the artist\'s availability.')
          return redirect(url_for('create_shows'))

      show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print(f"Error creating show: {e}")
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
  else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
