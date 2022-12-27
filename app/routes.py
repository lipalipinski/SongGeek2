from datetime import datetime 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from werkzeug.urls import url_parse
from flask import flash, render_template, redirect, request, url_for
from flask_login import current_user, login_user, login_required, logout_user

from app import app
from app.helpers import dict_html, img_helper
from app.models import db, Playlist, Owner, Track, Album, Artist, Img, User
from app.forms import LoginForm

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10, retries=5)

pl_update_time = app.config["PLAYLIST_UPDATE"]


@app.route("/")
@app.route("/index")
def index():
    html = "hello, world"
    return render_template("index.html", html = html)


@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("playlist_manager"))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("invalid username or passowrd")
            return redirect(url_for("login"))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")

        # no next page or different domain 
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("playlist_manager")

        return redirect(next_page)

    return render_template("login.html", form = form)


@app.route("/logout")
def logout():
    
    logout_user()

    return redirect(url_for("index"))



@app.route("/add-playlist", methods = ["POST", "GET"])
@login_required
def add_playlist():

    # ======== POST handler ===========
    if request.method == "POST":
        
        # no playlist id provided 
        if not request.form.get("id"):
            msg = 'No playlist ID provided'
            flash(msg)
            return redirect(url_for("add_playlist"))
        

        pl_id = request.form.get("id")
        pl = Playlist.query.get(pl_id)
        
        
        if pl and pl.updated:
            #updated = datetime.strptime(pl.updated, "%b %d %H:%M:%S %Y")

            now = datetime.utcnow()
            if (now - pl.updated).seconds < pl_update_time:
                flash('Playlist up to date')
                return redirect(url_for("playlist_manager"))

        
        # spotify api request
        try:
            resp = spotify.playlist(pl_id)
        except Exception as inst:
            app.logger.info(inst)
            flash('Bad request')
            return redirect(url_for("playlist_manager"))           


        # check playlist snapshot
        if pl and pl.snapshot_id == resp["snapshot_id"]:
            flash('No changes to playlist, no need to update')
            return redirect(url_for("playlist_manager"))    

        if pl:
            db.session.delete(pl)

        # \\\\\\
        pl = Playlist(id=resp["id"], description=resp["description"], name=resp["name"], url=resp["external_urls"]["spotify"], snapshot_id=resp["snapshot_id"])

        # pl img
        img = img_helper(resp["images"])
        img = Img(sm=img["sm"], md=img["md"], lg=img["lg"])

        # ////////
        pl.img = img

        # check if owner in db
        ownr = Owner.query.get(resp["owner"]["id"])
        if not ownr:
            ownr = Owner(id=resp["owner"]["id"], name=resp["owner"]["display_name"], url=resp["owner"]["external_urls"]["spotify"])

        # \\\\\\\
        pl.owner = ownr

        # request tracks
        pl_items = spotify.playlist_items(pl_id)
        tracks = pl_items["items"]

        # request remaining tracks
        while pl_items["next"]:
            pl_items = spotify.next(pl_items)
            tracks.extend(pl_items["items"])

        # add new tracks to db
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
            pl.tracks.append(trck)
            

        # session add
        db.session.add(pl)

        # session commit
        db.session.commit()
        
        
        msg = 'Playlist added/updated'
        flash(msg)
        return redirect(url_for("playlist_manager"))

    # ======= GET handler ===========
    return redirect(url_for("playlist_manager"))


@app.route("/remove-playlist", methods = ["POST"])
@login_required
def remove_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    db.session.delete(pl)
    db.session.commit()

    flash("Playlist removed")
    return redirect(url_for("playlist_manager"))


@app.route("/playlist-manager", methods = ["POST", "GET"])
@login_required
def playlist_manager():


    plsts = Playlist.query.all()

    return render_template("playlist_manager.html", plsts = plsts)


@app.route("/playlist-manager/<playlist_id>")
@login_required
def playlist_detalis(playlist_id):


    plst = Playlist.query.get(playlist_id)
    
    return render_template("playlist_details.html", plst = plst)

        

@app.route("/test")
def test():

    playlists = spotify.playlist('37i9dQZF1DX6ujZpAN0v9r')
    return render_template("test.html", playlists = dict_html(playlists), raw = str(playlists))
