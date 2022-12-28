from flask import session, redirect, url_for

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


def auth_required(f):
    def decorated_function(*args, **kwargs):
        if session.get("toke") is None:
            return redirect(url_for("verify"))
        return f(*args, **kwargs)
    return decorated_function