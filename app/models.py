from app import db
from datetime import datetime


playlist_track = db.Table("playlist_track",
                db.Column("playlist_id", db.Text, db.ForeignKey("playlist.id"), primary_key=True),
                db.Column("track_id", db.Text, db.ForeignKey("track.id"), primary_key=True)
                )


track_artist = db.Table("track_artist",
                db.Column("track_id", db.Text, db.ForeignKey("track.id"), primary_key=True),
                db.Column("artist_id", db.Text, db.ForeignKey("artist.id"), primary_key=True)    
                )


album_artist = db.Table("album_artist", 
                db.Column("album_id", db.Text, db.ForeignKey("album.id"), primary_key=True),
                db.Column("artist_id", db.Text, db.ForeignKey("artist.id"), primary_key=True),
                )


class Playlist(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    snapshot_id = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Text, db.ForeignKey("owner.id")) 
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    tracks = db.relationship("Track", secondary=playlist_track, back_populates="playlists")

    def active_tracks(self):
        return sum(1 for tr in self.tracks if tr.prev_url)

    def total_tracks(self):
        return len(self.tracks)

    def __repr__(self) -> str:
        return f"<playlist: {self.name} by {self.owner_id}>"


class Owner(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    playlists = db.relationship("Playlist", backref="owner", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<owner: {self.name} id: {self.id}>"


class Track(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    album_id = db.Column(db.Text, db.ForeignKey("album.id"), nullable=False)
    url = db.Column(db.Text, nullable=False)
    prev_url = db.Column(db.Text)
    playlists = db.relationship("Playlist", secondary=playlist_track, back_populates="tracks")
    artists = db.relationship("Artist", secondary=track_artist, back_populates="tracks")


    def __repr__(self) -> str:
        return f"<track: {self.name}>"


class Album(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    tracks = db.relationship("Track", backref="album", lazy="dynamic")
    artists = db.relationship("Artist", secondary=album_artist, back_populates="albums")

    def __repr__(self) -> str:
        return f"<album: {self.name}>"


class Artist(db.Model):

    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    tracks = db.relationship("Track", secondary=track_artist, back_populates="artists")
    albums = db.relationship("Album", secondary=album_artist, back_populates="artists")

    def __repr__(self) -> str:

        return f"<artist: {self.name}>"


class Img(db.Model):

    id = db.Column(db.Integer, index=True, primary_key=True)
    sm = db.Column(db.Text, nullable=False)
    md = db.Column(db.Text, nullable=False)
    lg = db.Column(db.Text, nullable=False)
    playlist = db.relationship("Playlist", backref="img", lazy="dynamic")
    album = db.relationship("Album", backref="img", lazy="dynamic")
