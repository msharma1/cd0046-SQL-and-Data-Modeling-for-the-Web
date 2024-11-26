from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Moved to models.py for Separation of Concers.
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)  # City is required
    state = db.Column(db.String(120), nullable=False)  # State is required
    address = db.Column(db.String(120), nullable=False)  # Address is required
    phone = db.Column(db.String(120), nullable=False)  # Phone is required
    genres = db.Column(db.ARRAY(db.String), nullable=False)   # Genres is required
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - DONE
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)  # Add seeking_venue field
    seeking_description = db.Column(db.String(500))  # Add seeking_description field 
    # Relationships
    shows = db.relationship('Show', backref='venue', lazy=True)  # Define relationship to Show model

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)  # Name is required and unique
    city = db.Column(db.String(120), nullable=False)  # City is required
    state = db.Column(db.String(120), nullable=False)  # State is required
    phone = db.Column(db.String(120), nullable=False)  # Phone is required
    genres = db.Column(db.ARRAY(db.String), nullable=False)  # Genres is required
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - DONE
    website = db.Column(db.String(120))
    # Add website field
    seeking_venue = db.Column(db.Boolean, default=False)  # Add seeking_venue field
    seeking_description = db.Column(db.String(500))  # Add seeking_description field
    # Attempting BONUS task of having artist availability
    available_times = db.Column(db.ARRAY(db.String))  # Add available_times field
    # Relationships
    shows = db.relationship('Show', backref='artist', lazy=True)  # Define relationship to Show model


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. - DONE
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id}>' 