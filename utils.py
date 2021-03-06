from functools import wraps

import msal
from flask import session, url_for

import app_config


class AuthError(Exception):
    """basic auth exception"""
    pass


try:
    from werkzeug.exceptions import HTTPException

    class NotAuthenticatedError(HTTPException, AuthError):
        code = 401
        status = 401
        description = 'User is not authenticated'
except ImportError:
    class NotAuthenticatedError(AuthError):
        code = 401
        status = 401
        description = 'User is not authenticated'


def load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def build_auth_code_flow(authority=None, scopes=None):
    return build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def get_token_from_cache(scope=None, default_scope=False):
    cache = load_cache()  # This web app maintains one cache per session
    cca = build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(
            app_config.SCOPE if default_scope else scope,
            account=accounts[0]
            )
        save_cache(cache)
        return result


def login_required(f):
    """@decorator to ensure user is authenticated"""
    @wraps(f)
    def assert_login(*args, **kwargs):
        token = get_token_from_cache(app_config.SCOPE)
        if not token:
            raise NotAuthenticatedError
        # TODO: check if ID token is expired
        # if it is, take user to get re-authenticated.
        # TODO: upon returning from re-auth, user should get back to
        # where they were trying to go.
        return f(*args, **kwargs)
    return assert_login


def get_graph_api_url(path='') -> str:
    return app_config.GRAPH_ENDPOINT + path
