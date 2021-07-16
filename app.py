#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from sqlalchemy.orm import relationship
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  city_states = Venue.query.with_entities(Venue.state,
    Venue.city).group_by(Venue.state, Venue.city).all()

  data = []

  for c in city_states:
      venues = Venue.query.filter_by(city = c.city).filter_by(
        state = c.state).all()

      data.append({
        "city": c.city,
        "state": c.state,
        "venues": venues
      })

  return render_template('pages/venues.html', city_states=city_states, data=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: (DONE) implement search on artists with partial string search. Ensure it is case-insensitive.
  search_key=request.form.get('search_term', '')

  response = Venue.query.filter(
        func.lower(Venue.name).contains(func.lower(search_key))
    ).all()

  data_structure={
    "count": len(response),
    "data": response
  }
  return render_template('pages/search_venues.html', results=data_structure,
    search_term=search_key)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: (DONE) NEED TO CREATE AND SHOW SHOWS, replace with real venue data from the venues table, using venue_id

  venue_info = Venue.query.filter_by(id = venue_id).all()
  past_shows = db.session.query(Show).join(
    Artist, Show.artist_id==Artist.id).join(
    Venue, Show.venue_id==Venue.id).filter(
    and_(Show.start_time<datetime.date.today(), Venue.id==venue_id)).with_entities(
        Venue.id.label('venue_id'),
        Artist.id.label('artist_id'),
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link'),
        Show.start_time.label('start_time')).order_by(Show.start_time).all()

  upcoming_shows = db.session.query(Show).join(
    Artist, Show.artist_id==Artist.id).join(
        Venue, Show.venue_id==Venue.id).filter(
        and_(Show.start_time>=datetime.date.today(), Venue.id==venue_id)).with_entities(
            Venue.id.label('venue_id'),
            Artist.id.label('artist_id'),
            Venue.name.label('venue_name'),
            Artist.name.label('artist_name'),
            Artist.image_link.label('artist_image_link'),
            Show.start_time.label('start_time')).order_by(
            Show.start_time).all()

  data={
    "info": venue_info[0],
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  # TODO: (DONE) insert form data as a new Venue record in the db, instead
  error = False
  form = VenueForm(request.form)
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET','POST'])
def delete_venue(venue_id):
  # TODO: (DONE) Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred, record not deleted.')
  if not error:
      flash('Record deleted...')

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: (DONE) replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: (DONE) implement search on artists with partial string search. Ensure it is case-insensitive.
  search_key=request.form.get('search_term', '')
  response = Artist.query.filter(func.lower(Artist.name).contains(
    func.lower(search_key))).all()

  data_structure={
    "count": len(response),
    "data": response
  }

  return render_template('pages/search_artists.html', results=data_structure, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_info = Artist.query.filter_by(id = artist_id).all()

  past_shows = db.session.query(Show).join(
    Artist, Show.artist_id==Artist.id).join(
    Venue, Show.venue_id==Venue.id).filter(
    and_(Show.start_time<datetime.date.today(), Artist.id==artist_id)).with_entities(
        Venue.id.label('venue_id'),
        Artist.id.label('artist_id'),
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Venue.image_link.label('venue_image_link'),
        Show.start_time.label('start_time')).order_by(Show.start_time).all()

  upcoming_shows = db.session.query(Show).join(
    Artist, Show.artist_id==Artist.id).join(
    Venue, Show.venue_id==Venue.id).filter(
    and_(Show.start_time>=datetime.date.today(), Artist.id==artist_id)).with_entities(
        Venue.id.label('venue_id'),
        Artist.id.label('artist_id'),
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Venue.image_link.label('venue_image_link'),
        Show.start_time.label('start_time')).order_by(Show.start_time).all()

  data={
    "info": artist_info[0],
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

  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)

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
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('Error occurred, artist not updated.')
  if not error:
      flash('Artist updated successfully!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)

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

  # TODO: DONE populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('Error occurred, venue not updated.')
  if not error:
      flash('Venue updated successfully!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: DONEreplace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #show_list = db.session.query(Artist, Venue, Show).with_entities(Venue.id.label('venue_id'), Artist.id.label('artist_id'), Venue.name.label('venue_name'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time.label('start_time'))

  show_list = db.session.query(Show).join(
    Artist, Show.artist_id==Artist.id).join(
    Venue, Show.venue_id==Venue.id).with_entities(
        Venue.id.label('venue_id'),
        Artist.id.label('artist_id'),
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link'),
        Show.start_time.label('start_time')).order_by(Show.start_time).all()

  return render_template('pages/shows.html', shows=show_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)
  try:
      show = Show()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
  if not error:
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
