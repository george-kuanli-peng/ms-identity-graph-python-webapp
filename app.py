import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session

import app_config
from blueprints.me import me_bp
from utils import (NotAuthenticatedError,
                   build_auth_code_flow, build_msal_app, get_token_from_cache,
                   load_cache, login_required, save_cache)


app = Flask(__name__)
app.config.from_object(app_config)
Session(app)
app.register_error_handler(
    NotAuthenticatedError,
    lambda err: (render_template('auth_401_error.html'), err.code)
)
app.register_blueprint(me_bp, url_prefix='/me')

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"])


@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])


@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = load_cache()
        result = build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


@app.route("/graphcall")
@login_required
def graphcall():
    token = get_token_from_cache(app_config.SCOPE)
    graph_data = requests.get(  # Use token to call downstream service
        app_config.GRAPH_ENDPOINT + '/users',
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


app.jinja_env.globals.update(_build_auth_code_flow=build_auth_code_flow)

if __name__ == "__main__":
    app.run()
