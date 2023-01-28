import random
import requests
import spotipy
import statistics
import pandas as pd
from os import getenv
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from flask_login import UserMixin
from app import app, db, login, spotify, pl_update_time, cache
from app.helpers import img_helper, retryfy
from sqlalchemy import func


@cache.cached(timeout=3600, key_prefix="pls_avgs")
def all_pls_avgs():
    '''returns a list of all playlists average scores'''
    app.logger.debug("all_pls_avgs not cached")
    return [pl.avg_score() for pl in db.session.query(Playlist).all() if pl.avg_score() != 0]

def get_ranking(n=None):
    """get to n players returns sorted dict {<user>:rank, ...}"""
    ids = []
    pts = []
    for user in db.session.query(User).all():
        ids.append(user)
        pts.append(user.total_points)

    sr = pd.Series(pts)
    sr.index = ids

    ranking = sr.rank(ascending=False, method="first", na_option="bottom").sort_values().head(n).to_dict()

    return ranking

@login.user_loader
def load_user(id):
    return User.query.get(id)


class User(UserMixin, db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    token = db.Column(db.Text)
    r_token =  db.Column(db.Text)
    expires = db.Column(db.DateTime)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    admin = db.Column(db.Boolean, default = False)
    name = db.Column(db.Text)
    img_id = db.Column(db.Integer, db.ForeignKey("img.id"))
    total_points = db.Column(db.Integer, default = 0)
    games = db.relationship("Game", backref="user", lazy="dynamic")
    quests = db.relationship("Quest", secondary="game", viewonly=True)

    def __repr__(self) -> str:
        return f"<user: {self.name}>"

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
        except Exception as err:
            app.logger.error(f"token refresh error: {err}")
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
        
        try:
            # add track tolibrary
            if like:
                sp.current_user_saved_tracks_add([track_id])
            # remove
            else:
                sp.current_user_saved_tracks_delete([track_id])
        except Exception as err:
            app.logger.error(f"User.set_like error: {err}")
            raise RequestException from err
        
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

        # minimum number of plays = average number of one song plays
        tracks = [track for track in tracks.values() if track["q"] > 1]
        if len(tracks) == 0:
            return []
        trcks_plays = [track["q"] for track in tracks]
        played_at_least = statistics.mean(trcks_plays)
    
        top_tracks = [{"track":trck["trck"], "score": round(trck["p"]/trck["q"], 2)} for trck in tracks if not trck["q"] < played_at_least]
        top_tracks.sort(key = lambda track : track["score"], reverse=True)

        return top_tracks

    @cache.memoize(timeout=60)
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

        if len(artists) == 0:
            return []
        
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
            if playlist.id not in playlists:
                playlists[playlist.id] = dict()
                playlists[playlist.id]["plst"]= playlist
                playlists[playlist.id]["q"] = 1
                playlists[playlist.id]["p"] = game.points()
            else:
                playlists[playlist.id]["q"] += 1
                playlists[playlist.id]["p"] += game.points()

        if len(playlists) == 0:
            return []
        
        played_at_least = statistics.median([pl["q"] for pl in playlists.values()])
        top_playlists = [{"plst":plst["plst"], "score":round(plst["p"]/plst["q"], 2)} for plst in playlists.values() if not plst["q"] <= played_at_least]
        top_playlists.sort(key = lambda playlist : playlist["score"], reverse=True)
        return top_playlists

    @cache.memoize(timeout=5)
    def count_games(self):
        games = db.session.query(Game).filter(Game.user_id == self.id, Game.status == 5).count()
        return games

    @cache.memoize(timeout=5)
    def answers(self):
        """ returns (correct_answers, all_answers) """
        # consider only finished games (Game.status == 5)
        answers = db.session.query(Quest).join(Game).join(User).filter(User.id == self.id, Game.status == 5)
        all_quests = answers.count()
        corr_answers = answers.filter(Quest.points != 0).count()
        return (corr_answers, all_quests)

    def set_total_points(self):
        self.total_points = sum([game.final_points for game in self.games if game.final_points != None])

    def rank(self):
        return get_ranking()[self]

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
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    playlist_id = db.Column(db.Text, db.ForeignKey("playlist.id"))
    status = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer)
    final_points = db.Column(db.Integer)
    quests = db.relationship("Quest", backref="game", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)

    def init_quests(self):

        try:
            tracks = random.sample(self.playlist.active_list(), 5)
        except ValueError as err:
            raise ValueError(f"Game.init_quest fail, Game.id={self.id}: {err}")
            
        
        for i, track in enumerate(tracks):
            self.quests.append(Quest(track_id = track.id, q_num = i))
        
        return True

    def update_status(self):
        self.status +=1
        if self.status == 5:
            lvl_mod = {1:0.5, 2:1, 3:2}
            self.final_points = round(self.points() * lvl_mod[self.level], 0)
            self.user.set_total_points()

    def current_quest(self):
        app.logger.debug(f"game: {self.id}/{self.status}")
        if self.status in range(0, 5):
            return db.session.get(Quest, {"game_id":self.id, "q_num":self.status})
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
        return [track for track in self.tracks if track.prev_url != None]

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

    @retryfy(3, 3)
    def update(self, force=False):
        """ force = force update """

        if self.updated and not force:
            now = datetime.utcnow()
            delta = (now - self.updated)
            if self.updated and delta.seconds < pl_update_time and delta.days < 1:
                # playlist up to date
                return True
        
        # spotify request
        try:
            resp = spotify.playlist(self.id)
        except Exception as err:
            raise RequestException(f"Playlist request failed: {err}")

        self.updated = datetime.utcnow()
        # check snapshot
        if self.snapshot_id and self.snapshot_id == resp["snapshot_id"] and not force:
            db.session.flush()
            return True

        app.logger.debug(f"start playlist update id: {self.id}")

        app.logger.debug(f"old img: {self.img}")
        # update description, name, url, img, owner
        self.preload(resp)
        db.session.flush()

        # request tracks
        try:
            pl_items = spotify.playlist_items(self.id)
        except Exception as err:
            raise RequestException(f"Playlist update fail (get items): {err}")
            
        
        tracks = pl_items["items"]

        # request remaining tracks
        while pl_items["next"]:
            try:
                pl_items = spotify.next(pl_items)
            except Exception as err:
                raise RequestException(f"Additional items request failed: {err}")
            tracks.extend(pl_items["items"])

        # add new tracks to db
        self.tracks.clear()
        for track in tracks:
            track = track["track"]

            # sometimes spotify gives empty "tracks"
            if not track or not track["preview_url"]:
                app.logger.debug(f"TRACK NOT ACTIVE \n")
                continue

            # check if track in db
            trck = Track.query.get(track["id"])
            if not trck:
                trck = Track(id=track["id"], name=track["name"], album_id=track["album"]["id"], url=track["external_urls"]["spotify"], prev_url=track["preview_url"])
            
            # artists from track to tb
            trck.artists.clear()
            for artist in track["artists"]:
                with db.session.no_autoflush:
                    artst = Artist.query.get(artist["id"])
                if not artst:
                    artst = Artist(id=artist["id"], name=artist["name"], url=artist["external_urls"]["spotify"])
                    db.session.add(artst)
                    #db.session.flush()

                # \\\\\\\\\\\
                trck.artists.append(artst)

            # add new albums to db
            with db.session.no_autoflush:
                albm = db.session.get(Album, track["album"]["id"])
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

        db.session.flush()
        #db.session.commit()

        return True

    def last_update(self):
        if not self.updated:
            return "preloaded"
        delta = datetime.utcnow() - self.updated
        days = delta.days
        hrs = delta.seconds//3600
        mins = (delta.seconds - hrs*3600)//60
        upt_txt = f"d:{days} h:{hrs} m:{mins}"
        return upt_txt

    def avg_score(self, user=None):
        """ returns current average score of all games with this playlist, 
        or 0 if no games played"""
        
        games_count = db.session.query(Game).filter(Game.playlist_id == self.id).count()
        if games_count == 0:
            return 0
        if not user:
            return sum([game.points() for game in self.games])/games_count
       
        user_games = db.session.query(Game).filter(Game.playlist_id == self.id, Game.user_id == user.id)
        return statistics.mean([game.points() for game in user_games.all()])


    @cache.memoize(timeout=600)
    def level(self):

        if self.avg_score() == 0:
            return 2
        
        all_scores = all_pls_avgs()
        #stddec needs at least two data points
        if len(all_scores) < 2:
            return 2
        
        mean_score = statistics.mean(all_scores)
        std_dev = statistics.stdev(all_scores)

        # easy
        if self.avg_score() > mean_score + 0.5 * std_dev:
            return 1
        # hard
        elif self.avg_score() < mean_score - 0.5 * std_dev:
            return 3
        # medium
        return 2

    def __repr__(self) -> str:
        return f"<playlist: {self.name} by {self.owner_id}>"


class Owner(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text)
    playlists = db.relationship("Playlist", backref="owner", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<owner: {self.name} id: {self.id}>"


class Track(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    album_id = db.Column(db.Text, db.ForeignKey("album.id"))
    url = db.Column(db.Text)
    prev_url = db.Column(db.Text)
    playlists = db.relationship("Playlist", secondary=playlist_track, back_populates="tracks")
    artists = db.relationship("Artist", secondary=track_artist, back_populates="tracks")
    quests = db.relationship("Quest", backref="track", lazy="dynamic")


    def __repr__(self) -> str:
        return f"<track: {self.name}>"


class Album(db.Model):
    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text)
    img_id = db.Column(db.Integer, db.ForeignKey("img.id")) 
    tracks = db.relationship("Track", backref="album", lazy="dynamic")
    artists = db.relationship("Artist", secondary=album_artist, back_populates="albums")

    def __repr__(self) -> str:
        return f"<album: {self.name}>"


class Artist(db.Model):

    id = db.Column(db.Text, index=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text)
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

    def __repr__(self) -> str:
        return f"img: {self.id}, sm: {self.sm}, md: {self.md}, lg: {self.lg}"
