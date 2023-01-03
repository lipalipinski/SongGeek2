from datetime import datetime
from requests.exceptions import RequestException
from flask_login import UserMixin
from app import db, login, spotify, pl_update_time
from app.helpers import img_helper

@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(UserMixin, db.Model):
    id = db.Column(db.Text, primary_key=True)
    token = db.Column(db.Text)
    r_token =  db.Column(db.Text)
    expires = db.Column(db.DateTime)
    admin = db.Column(db.Boolean, default = False)
    name = db.Column(db.Text)


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
    snapshot_id = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, default=False)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Text, db.ForeignKey("owner.id")) 
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    tracks = db.relationship("Track", secondary=playlist_track, back_populates="playlists")

    def active_tracks(self):
        return sum(1 for tr in self.tracks if tr.prev_url)

    def total_tracks(self):
        return len(self.tracks)

    def update(self):
        
        now = datetime.utcnow()
        if self.updated and (now - self.updated).seconds < pl_update_time:
            raise ValueError("Playlist up to date")

        # spotify request
        try:
            resp = spotify.playlist(self.id)
        except:
            raise RequestException("Spotify request failed")

        # check snapshot
        if self.snapshot_id and self.snapshot_id == resp["snapshot_id"]:
            self.updated = datetime.utcnow()
            return True

        # pl img
        img = img_helper(resp["images"])
        self.img = Img(sm=img["sm"], md=img["md"], lg=img["lg"])

        # check if owner in db
        ownr = Owner.query.get(resp["owner"]["id"])
        if not ownr:
            ownr = Owner(id=resp["owner"]["id"], name=resp["owner"]["display_name"], url=resp["owner"]["external_urls"]["spotify"])
        self.owner = ownr

        # request tracks
        pl_items = spotify.playlist_items(self.id)
        tracks = pl_items["items"]

        # request remaining tracks
        while pl_items["next"]:
            pl_items = spotify.next(pl_items)
            tracks.extend(pl_items["items"])

        # add new tracks to db
        self.tracks.clear()
        for track in tracks:
            track = track["track"]

            # check if track in db
            trck = Track.query.get(track["id"])
            if not trck:
                trck = Track(id=track["id"], name=track["name"], album_id=track["album"]["id"], url=track["external_urls"]["spotify"], prev_url=track["preview_url"])
            
            # artists from track to tb
            trck.artists.clear()
            for artist in track["artists"]:
                artst = Artist.query.get(artist["id"])
                if not artst:
                    artst = Artist(id=artist["id"], name=artist["name"], url=artist["external_urls"]["spotify"])
                    db.session.add(artst)
                    db.session.flush()

                # \\\\\\\\\\\
                trck.artists.append(artst)

            # add new albums to db
            albm = Album.query.get(track["album"]["id"])
            if not albm:
                albm = Album(id=track["album"]["id"], name=track["album"]["name"], url=track["album"]["external_urls"]["spotify"]) 
                # \\\\\\\\\\\
                img = img_helper(track["album"]["images"])
                albm.img = Img(sm=img["sm"], md=img["md"], lg=img["lg"])
                db.session.add(albm)
                db.session.flush()

            # artists from album
            albm.artists.clear()
            for artist in track["album"]["artists"]:
                artst = Artist.query.get(artist["id"])
                if not artst:
                    artst = Artist(id=artist["id"], name=artist["name"], url=artist["external_urls"]["spotify"])
                    db.session.add(artst)
                    db.session.flush()

                # \\\\\\\\\\
                albm.artists.append(artst)

            # \\\\\\\\\\    
            trck.album = albm

            # \\\\\\\\\\\
            self.tracks.append(trck)


        self.updated = datetime.utcnow()
        return True

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
