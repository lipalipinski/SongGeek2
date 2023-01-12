import random
import requests
import spotipy
import statistics
from os import getenv
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from flask_login import UserMixin
from app import app, db, login, spotify, pl_update_time
from app.helpers import img_helper

@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(UserMixin, db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    token = db.Column(db.Text)
    r_token =  db.Column(db.Text)
    expires = db.Column(db.DateTime)
    admin = db.Column(db.Boolean, default = False)
    name = db.Column(db.Text)
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    games = db.relationship("Game", backref="user", lazy="dynamic")
    quests = db.relationship("Quest", secondary="game", viewonly=True)

    def __repr__(self) -> str:
        return f"<quest: {self.name}>"

    def refresh_token(self):

        # return if token is fresh
        if datetime.utcnow() + timedelta(seconds=app.config['TOKEN_UPDATE']) < self.expires:
            return True

        auth_token_url = f"{app.config['API_BASE']}/api/token/"
        try:
            res = requests.post(auth_token_url, data = {
            "grant_type":"refresh_token",
            "refresh_token":self.r_token,
            "client_id":getenv("SPOTIPY_CLIENT_ID"),
            "client_secret":getenv("SPOTIPY_CLIENT_SECRET")
            })
            res.raise_for_status()
        except:
            raise RequestException

        res = res.json()
        self.token = res["access_token"]
        if "refresh_token" in res.keys():
            self.r_token = res["refresh_token"]
        self.expires = datetime.utcnow() + timedelta(seconds=res["expires_in"])
        db.session.flush()
        db.session.commit()

        return True

    def likes_status(self, tracks):
        """ returns list of dict id:id, like:bool """
        sp = spotipy.Spotify(auth=self.token)
        likes = sp.current_user_saved_tracks_contains(tracks)
        id_likes = []
        for i, track in enumerate(tracks):
            id_likes.append({"id":track, "like":likes[i]})
        return id_likes

    def set_like(self, track_id, like):
        """ add/remove track from library """
        sp = spotipy.Spotify(auth=self.token)

        # add
        if like:
            try:
                sp.current_user_saved_tracks_add([track_id])
            except:
                raise RequestException
        # remove
        else:
            try:
                sp.current_user_saved_tracks_delete([track_id])
            except:
                raise RequestException
        
        return True

    def top_tracks(self):
        """ returns [{'track':plst, 'score':score}, ...] """
        tracks = dict()
        for quest in self.quests:
            track = quest.track
            if track.id not in tracks:
                tracks[track.id] = dict()
                tracks[track.id]["trck"] = track
                tracks[track.id]["q"] = 1
                tracks[track.id]["p"] = quest.points
            else:
                tracks[track.id]["q"] += 1
                tracks[track.id]["p"] += quest.points

        # minimum number of plays
        played_at_least = sum([track["q"] for track in tracks.values()]) / len(tracks)
        # top tracks are track asked more than 3 times
        top_tracks = [{"track":trck["trck"], "score": round(trck["p"]/trck["q"], 2)} for trck in tracks.values() if not trck["q"] <= played_at_least]
        top_tracks.sort(key = lambda track : track["score"], reverse=True)
            
        return top_tracks

    def top_artists(self):
        """ returns [{'artst':plst, 'score':score}, ...] """
        # minimum number of plays

        artists = dict()
        for quest in self.quests:
            for artist in quest.track.artists:
                if artist.id not in artists:
                    artists[artist.id] = dict()
                    artists[artist.id]["artst"] = artist
                    artists[artist.id]["q"] = 1
                    artists[artist.id]["p"] = quest.points
                else:
                    artists[artist.id]["q"] += 1
                    artists[artist.id]["p"] += quest.points

        played_at_least = sum([artist["q"] for artist in artists.values()]) / len(artists)
        top_artists = [{"artst":artst["artst"], "score": round(artst["p"]/artst["q"], 2)} for artst in artists.values() if not artst["q"] <= played_at_least]
        top_artists.sort(key = lambda artist : artist["score"], reverse=True)

        return top_artists
    
    def top_playlists(self):
        """ returns [{'plst':plst, 'score':score}, ...] """

        playlists = dict()
        games = self.games.filter(Game.status == 5)
        for game in games:
            playlist = game.playlist
            #print(playlist)
            if playlist.id not in playlists:
                playlists[playlist.id] = dict()
                playlists[playlist.id]["plst"]= playlist
                playlists[playlist.id]["q"] = 1
                playlists[playlist.id]["p"] = game.points()
            else:
                playlists[playlist.id]["q"] += 1
                playlists[playlist.id]["p"] += game.points()

        played_at_least = statistics.median([pl["q"] for pl in playlists.values()])
        print(played_at_least)
        top_playlists = [{"plst":plst["plst"], "score":round(plst["p"]/plst["q"], 2)} for plst in playlists.values() if not plst["q"] <= played_at_least]
        top_playlists.sort(key = lambda playlist : playlist["score"], reverse=True)
        return top_playlists


    def count_games(self):
        games = db.session.query(Game).filter(Game.user_id == self.id).count()
        return games


    def answers(self):
        """ returns (correct_answers, all_answers) """
        # consider only finished games (Game.status == 5)
        answers = db.session.query(Quest).join(Game).join(User).filter(User.id == self.id, Game.status == 5)
        all_quests = answers.count()
        corr_answers = answers.filter(Quest.points != 0).count()
        return (corr_answers, all_quests)


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


class Game(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    user_id = db.Column(db.Text, db.ForeignKey("user.id"), index=True)
    playlist_id = db.Column(db.Text, db.ForeignKey("playlist.id"))
    status = db.Column(db.Integer, default=0)
    quests = db.relationship("Quest", backref="game", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        db.session.flush()
        tracks = random.sample(Playlist.query.get(self.playlist_id).active_list(), 5)
        for i, track in enumerate(tracks):
            self.quests.append(Quest(track_id = track.id, q_num = i))

    def next_quest(self):
        
        if self.status in range(0, 5):
            return self.quests[self.status]
        return False

    def points(self):
        return sum([x.points for x in self.quests])


class Quest(db.Model):
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), index=True, primary_key=True)
    track_id = db.Column(db.Text, db.ForeignKey("track.id"), index=True)
    q_num = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    user = db.relationship("User", secondary="game", viewonly=True)

    def all_answrs(self):
        """ returns a list of four track (one being target track) 
        in random order"""

        tracks = [self.track]
        while len(tracks) < 4:
            track = random.choice(self.game.playlist.tracks)
            if track not in tracks:
                tracks.append(track)
        
        random.shuffle(tracks)
        return tracks

    def __repr__(self) -> str:
        return f"<quest: {self.track}, {self.game.user}>"


class Playlist(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.Text)
    url = db.Column(db.Text)
    snapshot_id = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, default=True)
    updated = db.Column(db.DateTime)
    owner_id = db.Column(db.Text, db.ForeignKey("owner.id")) 
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    tracks = db.relationship("Track", secondary=playlist_track, back_populates="playlists")
    games = db.relationship("Game", backref="playlist", lazy="dynamic")

    def active_tracks(self):
        return sum(1 for tr in self.tracks if tr.prev_url)

    def active_list(self):
        return [track for track in self.tracks if track.prev_url]

    def total_tracks(self):
        return len(self.tracks)

    def preload(self, resp):
        self.description = resp["description"]
        self.name=resp["name"]
        self.url=resp["external_urls"]["spotify"]

        img = img_helper(resp["images"])
        self.img = Img(sm=img["sm"], md=img["md"], lg=img["lg"])

        # check if owner in db
        ownr = Owner.query.get(resp["owner"]["id"])
        if not ownr:
            ownr = Owner(id=resp["owner"]["id"], name=resp["owner"]["display_name"], url=resp["owner"]["external_urls"]["spotify"])
        self.owner = ownr

        return True

    def update(self):
        
        if self.updated:
            now = datetime.utcnow()
            delta = (now - self.updated)
            if self.updated and delta.seconds < pl_update_time and delta.days < 1:
                return True

        # spotify request
        try:
            resp = spotify.playlist(self.id)
        except:
            return False

        # check snapshot
        if self.snapshot_id and self.snapshot_id == resp["snapshot_id"]:
            self.updated = datetime.utcnow()
            db.session.flush()
            return True

        #update snapshot_id
        self.snapshot_id = resp["snapshot_id"]

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

    def last_update(self):
        delta = datetime.utcnow() - self.updated
        days = delta.days
        hrs = delta.seconds//3600
        mins = (delta.seconds - hrs*3600)//60
        upt_txt = f"d:{days} h:{hrs} m:{mins}"
        return upt_txt

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
    quests = db.relationship("Quest", backref="track", lazy="dynamic")


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
    user = db.relationship("User", backref="img", lazy="dynamic")
