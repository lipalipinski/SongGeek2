from datetime import datetime 
from werkzeug.urls import url_parse
from flask import flash, render_template, redirect, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from requests.exceptions import RequestException

from app import app, spotify
from app.helpers import dict_html
from app.models import db, Playlist, Owner, Track, Album, Artist, Img, User
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    
    plsts = Playlist.query.filter_by(active=1).all()

    return render_template("index.html", plsts = plsts)


@app.route("/quiz")
def quiz():

    pl = Playlist.query.get(request.args.get("playlist_id"))

    return render_template("quiz.html", pl = pl)


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
        
        # spotify api request
        try:
            resp = spotify.playlist(pl_id)
        except Exception as inst:
            app.logger.info(inst)
            flash('Bad request')
            return redirect(url_for("playlist_manager"))           

        if not pl:
            pl = Playlist(id=resp["id"], description=resp["description"], name=resp["name"], url=resp["external_urls"]["spotify"])
            
        try:
            pl.update()
            db.session.add(pl)
            db.session.commit()
        except RequestException as err:
            flash(str(err))
            return redirect(url_for("playlist_manager"))
        except ValueError as err:
            flash(str(err))
            return redirect(url_for("playlist_manager"))
        
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


@app.route("/playlist_manager/activate", methods = ["POST", "GET"])
@login_required
def activate_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    pl.active = 1
    db.session.commit()

    return redirect(url_for("playlist_manager"))


@app.route("/playlist_manager/deactivate", methods = ["POST", "GET"])
@login_required
def deactivate_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    pl.active = 0
    db.session.commit()

    return redirect(url_for("playlist_manager"))


@app.route("/playlist_manager/update", methods=["POST", "GET"])
@login_required
def update_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    
    try:
        pl.update()
        db.session.add(pl)
        db.session.commit()
    except RequestException as err:
        flash(str(err))
        return redirect(url_for("playlist_manager"))
    except ValueError as err:
        flash(str(err))
        return redirect(url_for("playlist_manager"))

    flash("Playlist updated")
    return redirect(url_for("playlist_manager"))


@app.route("/playlist-manager/<playlist_id>")
@login_required
def playlist_detalis(playlist_id):


    plst = Playlist.query.get(playlist_id)
    
    return render_template("playlist_details.html", plst = plst)

        

@app.route("/test")
def test():

    playlists = spotify.playlist('37i9dQZF1DX6ujZpAN0v9r')
    return render_template("test.html", playlists = dict_html(playlists), raw = str(playlists))
