from datetime import datetime, timedelta
from os import getenv
import spotipy
import requests
import json
from flask import flash, render_template, redirect, request, url_for, Response, session
from flask_login import current_user, login_user, login_required, logout_user
from requests.exceptions import RequestException
from app import app, spotify, cache
from app.helpers import dict_html, img_helper, set_country, available_markets, retryfy, admin_required
from app.models import db, Playlist, User, Game, Img, get_ranking

@app.route("/api_callback", methods=["GET"])
def api_callback():

    if request.args.get("error"):
        flash(f"Log in failed")
        return redirect(url_for("index"))
    
    # spotify Oauth2 code
    code = request.args.get("code")

    auth_token_url = f"{app.config['API_BASE']}/api/token/"

    res = requests.post(auth_token_url, data = {
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":app.config["REDIRECT_URI"],
        "client_id":getenv("SPOTIPY_CLIENT_ID"),
        "client_secret":getenv("SPOTIPY_CLIENT_SECRET")
    })

    res_body = res.json()

    token = res_body.get("access_token")
    r_token = res_body.get("refresh_token")
    expires_in = res_body.get("expires_in") #seconds
    
    try:
        sp = spotipy.Spotify(auth=token)
        usr = sp.current_user()
    except spotipy.exceptions.SpotifyException as err:
        if err.http_status == 403:
            flash(f"Login failed, contact developer to gain access")
        else:
            flash("Login failed")
        return redirect(url_for("index"))

    user = User.query.filter_by(id = usr["id"]).first()

    if not user:
        user = User(id=usr["id"])
    
    user.token = token
    user.r_token = r_token
    user.expires = datetime.utcnow() + timedelta(seconds=expires_in)
    user.name = usr["display_name"]
    img = img_helper(usr["images"])
    user.img = Img(sm=img["sm"], md=img["md"], lg=img["lg"])
    db.session.add(user)
    db.session.commit()

    login_user(user, remember=False)
    
    # set session country
    code = "PL"
    set_country(code)

    return redirect(url_for("index"))


@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    CLI = getenv('SPOTIPY_CLIENT_ID')
    auth_url = f'''{app.config["API_BASE"]}/authorize?client_id={CLI}&response_type=code&redirect_uri={app.config["REDIRECT_URI"]}&scope={app.config["SCOPE"]}&show_dialog={True}'''
    
    return redirect(auth_url)

@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("index"))


# ==== REFRESH TOKEN BEFORE REQUEST if user authenticated
@app.before_request
def refresh_user_token():
    if current_user.is_authenticated:
        try:
            current_user.refresh_token()
        except RequestException:
            flash("You have been logged out due to inactivity")
            return redirect(url_for("logout"))
    db.session.commit()

# ==== LOGOUT USER IF session["country"] is None
@app.before_request
def require_country():
    if current_user.is_authenticated:
        if not session["country"]:
            return redirect(url_for("logout"))

#@app.route("/index")
@app.route("/", methods=["POST", "GET"])
def index():

    @cache.memoize(timeout=1800)
    @retryfy(3, 2)
    def fetch_playlists(spoti, limit, code = None):
        return spoti.featured_playlists(limit=limit, country = code)

    if request.method == "POST" and request.json["mode"] == "featuredPlaylists":
        
        playlists = []

        try:
            if current_user.is_anonymous:
                resp = fetch_playlists(spotify, 20, "GB")

            elif session["country"]["code"] in available_markets().keys():
                resp = fetch_playlists(spotify, 20, session["country"]["code"])
        except Exception as err:
            #flash(f'Bad request {inst}')
            print(f'\n\n SPOTIFY FAIL {err} \n\n')
            return Response(status=401)

        raw_playlists = resp["playlists"]["items"]
        for pl in raw_playlists:

            new_pl = Playlist.query.get(pl["id"])
            if not new_pl:
                new_pl = Playlist(id=pl["id"])
                new_pl.preload(pl)
                db.session.add(new_pl)
                db.session.commit()

            playlists.append({"id": new_pl.id, "name": new_pl.name, 
                "description": new_pl.description, 
                "url": new_pl.url,
                "ownerName": new_pl.owner.name, 
                "ownerUrl": new_pl.owner.url, 
                "imgUrl": new_pl.img.md,
                "lvl": new_pl.level()
                })
        return Response(json.dumps(playlists), status=200)

    return render_template("featured.html", countries = available_markets())

@app.route("/country", methods=["POST"])
@login_required
def country():

    code = request.json["code"]
    # VALIDATE COUNTRY
    if code not in available_markets().keys():
        print(f"WRONG COUNTRY: {code}")
        return Response(status=401)

    set_country(code)
    resp = json.dumps(session["country"])
    return Response(resp, status=200)


@app.route("/ranking", methods=["POST", "GET"])
@login_required
def ranking():

    # GET 
    if request.method == "GET":
        return render_template("ranking.html")
    
    # POST
    ranks_raw = get_ranking(10)
    ranks = [{"rank":rank, 
            "name":user.name,
            "imgUrl":user.img.sm,
            "total":user.total_points,
            "current":(user == current_user)} for user, rank in ranks_raw.items()]
    if current_user not in ranks_raw.keys():
        ranks.append({"rank":current_user.rank(), 
            "name":current_user.name,
            "imgUrl":current_user.img.sm,
            "total":current_user.total_points,
            "current":True})
    return Response(json.dumps(ranks), 200)


@app.route("/user", methods=["GET", "POST"])
@app.route("/user/<items>", methods=["POST"])
@login_required
def user_details(items = None):

    if request.method == "POST":

        # top artists
        if items == "top-artists":
            artists = current_user.top_artists()
            if len(artists) > 5:
                artists = artists[0:5]
            artists = [{
                    "id":artist["artst"].id, 
                    "name":artist["artst"].name, 
                    "url":artist["artst"].url, 
                    "score":artist["score"]} for artist in artists]
            return Response(json.dumps(artists), status=200)

        # top tracks
        if items == "top-tracks":
            tracks = current_user.top_tracks()
            if len(tracks) > 5:
                tracks = tracks[0:5]
            tracks = [{
                    "rank":i+1, 
                    "id":track["track"].id, 
                    "name":track["track"].name,
                    "url":track["track"].url,
                    "prevUrl":track["track"].prev_url,
                    "artists":[{"name":artist.name, "url":artist.url} for artist in track["track"].artists], 
                    "score":track["score"],
                    "albumUrl":track["track"].album.url,
                    "albumImg":track["track"].album.img.sm} for i, track in enumerate(tracks)]
            return Response(json.dumps(tracks), status=200)

        # top playlists
        plsts_q = 6
        if items == "top-playlists":
            playlists = current_user.top_playlists()
            if len(playlists) > plsts_q:
                playlists = playlists[0:plsts_q]
            playlists = [{
                    "id":pl["plst"].id, 
                    "name":pl["plst"].name,
                    "url":pl["plst"].url,
                    "lvl":pl["plst"].level(),
                    "imgUrl":pl["plst"].img.lg,
                    "ownerUrl":pl["plst"].owner.url,
                    "ownerName":pl["plst"].owner.name,
                    'description':pl["plst"].description,
                    "score":pl["score"]} for pl in playlists]
            
            return Response(json.dumps(playlists), status=200)
    
    corr_answers, all_answers = current_user.answers()
    return render_template("user_details.html", corr_answers=corr_answers, all_answers=all_answers)


@app.route("/remove-user", methods=["GET", "POST"])
def remove_user():

    if current_user.is_anonymous:
        return redirect(url_for("index"))
    
    # POSt
    if request.method == "POST":
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        return redirect(url_for("index"))
    
    # GET
    return render_template("remove_user.html")

@app.route("/quiz")
@app.route("/quiz/<pl_id>", methods=["POST", "GET"])
@login_required
def quiz(pl_id = None, game = None):
    
    if pl_id == None:
        return redirect(url_for("index"))

    # render template
    if request.method == "GET":
        # force update
        if request.args.get("force") == "True":
            app.logger.info(f"Force playlist update (pl_id={pl_id})")
            pl = Playlist.query.get(pl_id)
            try:
                pl.update(force=True)
            except Exception as err:
                app.logger.critical(f"Playlist force update fail: {err}")
                return redirect(url_for("index"))
            
            db.session.add(pl)
            db.session.commit()
        return render_template("quiz.html", pl_id = pl_id)

    # ======= new game =========    
    if request.json["mode"] == "newGame":
        pl = Playlist.query.get(pl_id)
        
        # update playlist 
        pl.update()
        db.session.add(pl)
        db.session.commit()


        game = Game(user_id=current_user.id, playlist = pl, level = pl.level())
        db.session.flush()
        try:
            game.init_quests()
        except ValueError as err:
            app.logger.critical(f"init_quest error: {err}")
            db.session.rollback()
            return Response(500)
        db.session.add(game)
        db.session.commit()

        next_quest = game.next_quest()
        db.session.add(game)
        db.session.commit()

        body = {
                "gameId": game.id,
                "quest_num":0, 
                "plImgUrl":pl.img.md, 
                "plDescription":pl.description,
                "plName":pl.name,
                "plOwner":pl.owner.name,
                "plLvl":game.level}

        body["next_url"] = next_quest.track.prev_url
        next_tracks = []
        for track in next_quest.all_answrs():
            next_tracks.append({"id":track.id, "name":track.name})
        body["next_tracks"] = next_tracks

        return Response(json.dumps(body), 200)


    #  ==== answer received ======
    elif request.json["mode"] == "nextQuest":

        game_id = request.json["gameId"]
        track_id = request.json["id"]
        score = request.json["score"]
        game = Game.query.filter_by(id=game_id).first()
        quest = game.quests[game.status]
        red = ''

        if quest.track_id == track_id:
            quest.points = score +1
            db.session.flush()
        else:
            red = track_id
        game.update_status()
        db.session.commit()

        next_quest = game.next_quest()
        body = {
                "quest_num":game.status,
                "total_points":game.points(),
                "points":quest.points,
                "green":quest.track_id,
                "red":red,
                }
        if next_quest:
            next_tracks =[]
            next_url = next_quest.track.prev_url
            next_url = next_quest.track.prev_url
            for track in next_quest.all_answrs():
                next_tracks.append({"id":track.id, "name":track.name})
            body["next_url"] = next_url
            body["next_tracks"] = next_tracks
        else:
            
            body["next_url"] = ""
            body["resultsUrl"] = url_for("quiz_results", pl_id = pl_id, game = game.id)

        return Response(json.dumps(body), 200)
    
    else:
        return Response(401)


@app.route("/quiz/<pl_id>/<game>", methods=["GET"])
@login_required
def quiz_results(pl_id, game):
    pl = Playlist.query.get(pl_id)
    game = db.session.query(Game).get(game)
    if not game or game.user_id != current_user.id:
        return redirect(url_for("index"))
    return render_template("quiz_score.html", pl = pl, game = game)


@app.route("/likes", methods=["POST"])
def likes():
    
    mode = request.json["mode"]

    # ==== check liked songs ===
    if mode == "check":
        tracks = request.json["tracks"]
        try:
            id_likes = current_user.likes_status(tracks)
        except:
            return{"status":401}

        body = json.dumps({"tracks":id_likes})
        return Response(body, status=200)

    # ==== set like =====
    elif mode == "set_like":
        track_id = request.json["id"]
        like = request.json["like"]
        
        try:
            current_user.set_like(track_id, like)
        except RequestException:
            return Response({}, status=401)

        body = json.dumps({"id":track_id, "like":like})
        return Response(body, status=200)

    return Response({}, status=401)



@app.route("/add-playlist", methods = ["POST", "GET"])
@login_required
@admin_required(current_user)
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
@admin_required(current_user)
def remove_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    db.session.delete(pl)
    db.session.commit()

    flash("Playlist removed")
    return redirect(url_for("playlist_manager"))


@app.route("/playlist-manager", methods = ["POST", "GET"])
@login_required
@admin_required(current_user)
def playlist_manager():


    plsts = Playlist.query.all()

    return render_template("playlist_manager.html", plsts = plsts)


@app.route("/playlist_manager/activate", methods = ["POST", "GET"])
@login_required
@admin_required(current_user)
def activate_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    pl.active = 1
    db.session.commit()

    return redirect(url_for("playlist_manager"))


@app.route("/playlist_manager/deactivate", methods = ["POST", "GET"])
@login_required
@admin_required(current_user)
def deactivate_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))
    pl.active = 0
    db.session.commit()

    return redirect(url_for("playlist_manager"))


@app.route("/playlist_manager/update", methods=["POST", "GET"])
@login_required
@admin_required(current_user)
def update_playlist():

    pl = Playlist.query.get(request.form.get("playlist_id"))

    pl.update()
    db.session.add(pl)
    db.session.commit()


    flash("Playlist updated")
    return redirect(url_for("playlist_manager"))


@app.route("/playlist-manager/<playlist_id>")
@login_required
@admin_required(current_user)
def playlist_detalis(playlist_id):


    plst = Playlist.query.get(playlist_id)
    
    return render_template("playlist_details.html", plst = plst)

        
