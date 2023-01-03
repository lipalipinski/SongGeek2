from flask import session, redirect, url_for
from app import app
from os import getenv
import requests

def dict_html(dct):
    html = ''
    if type(dct) == list:
        
        html += '<table class="table table-bordered table-striped">\n' 
        for item in dct:
            html += '<tr><td>' + dict_html(item) + '</td></tr>'
        html += '</table>\n'

    elif type(dct) == dict:
        html += '<table class="table table-bordered table-striped"><thead><tr>'
        for key in dct.keys():
            html += '<th>' + str(key) + '</th>'
        html += '</thead></tr><tbody><tr>'
        for value in dct.values():
            html += '<td>' + dict_html(value) + '</td>'
        html += '</tr></tbody></table>\n'

    else:
        return str(dct)
    return str(html)


def img_helper(images):
    """returns {sm: 'url', md: 'url', lg: 'url'}"""

    sm = images[::-1][0]["url"]
    md = images[int(len(images)/2)]["url"]
    lg = images[0]["url"]

    return {"sm": sm, "md": md, "lg": lg}

def refresh_token(refresh_token):

    auth_token_url = f"{app.config['API_BASE']}/api/token"

    res = requests.post(auth_token_url, data = {
        "grant_type":"refresh_token",
        "refresh_token":refresh_token,
        "client_id":getenv("SPOTIPY_CLIENT_ID"),
        "client_secret":getenv("SPOTIPY_CLIENT_SECRET")
    })

    res_body = res.json()
    if res_body.get("refresh_token"):
        res_body["refresh_token"] = refresh_token

    return res_body.get("access_token")
