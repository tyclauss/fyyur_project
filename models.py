from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    genres = db.Column(db.ARRAY(db.String()))

    # Relationship to shows, with a bidirectional backreference so venue attributes can be accessed via show.
    # back ref explanation (https://hackersandslackers.com/sqlalchemy-data-models/)
    shows = db.relationship("Show",
        backref="Venue",
        lazy="joined",
        cascade="all, delete"
    )

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    talent_search = db.Column(db.String(1000))
    seeking_venue =db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    genres = db.Column(db.ARRAY(db.String()))

    # Relationship to shows, with a bidirectional backreference so artist attributes can be accessed via show.
    # Thank you to my reviewer for the tips on lazy="joined" and cascade="all, delete".
    # --- didn't utilize this setup in this project but I'll have it for next time.
    shows = db.relationship("Show",
        backref="Artist",
        lazy="joined",
        cascade="all, delete"
    )

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
