"""
Google Sign-In verification + session handling for SaralDoc.

Flow:
  1. Frontend uses Google Identity Services JS to get an ID token after the
     user signs in with Google.
  2. Frontend POSTs that ID token to /auth/google.
  3. We verify the ID token directly with Google's servers (verify_google_token
     below) - this proves the token is real and tells us who the user is.
  4. We issue OUR OWN short session JWT (signed with SESSION_SECRET, a value
     only this server knows) and set it as an httponly cookie. The frontend
     never needs to see or manage the Google token again after this point -
     it just relies on the session cookie for every subsequent request.
  5. get_current_user() is a FastAPI dependency that reads + verifies that
     session cookie, for protecting any route.

Env vars required (see .env.example):
  GOOGLE_CLIENT_ID   - from Google Cloud Console (public, safe to expose)
  SESSION_SECRET     - random long string, used only server-side to sign
                        session cookies. Generate with:
                        python -c "import secrets; print(secrets.token_hex(32))"
"""
import os
import time
from typing import Optional

import jwt
from fastapi import Cookie, HTTPException, Response
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "")
SESSION_COOKIE_NAME = "saraldoc_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

_google_request = google_requests.Request()


def verify_google_token(credential: str) -> dict:
    """Verify a Google ID token (the `credential` string from Google
    Identity Services on the frontend) directly against Google's servers.
    Raises HTTPException(401) if the token is invalid, expired, or was
    issued for a different Client ID than ours."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: GOOGLE_CLIENT_ID is not set.",
        )
    try:
        info = id_token.verify_oauth2_token(
            credential, _google_request, GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        # Bad/expired/wrong-audience token - the token itself is invalid.
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")
    except Exception as e:
        # Anything else (e.g. couldn't reach Google's cert servers) is a
        # transient infra issue, not the user's fault - 503, not 401.
        raise HTTPException(
            status_code=503,
            detail=f"Could not verify Google token right now: {e}",
        )

    return {
        "sub": info["sub"],  # Google's stable unique user id
        "email": info.get("email", ""),
        "email_verified": info.get("email_verified", False),
        "name": info.get("name", ""),
        "picture": info.get("picture", ""),
    }


def create_session_token(user: dict) -> str:
    """Issue our own signed session JWT for a verified user."""
    if not SESSION_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: SESSION_SECRET is not set.",
        )
    now = int(time.time())
    payload = {
        "sub": user["sub"],
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
        "iat": now,
        "exp": now + SESSION_TTL_SECONDS,
    }
    return jwt.encode(payload, SESSION_SECRET, algorithm="HS256")


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,       # requires HTTPS in production; browsers allow
                            # this over http://localhost for local dev too
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


def get_current_user(
    saraldoc_session: Optional[str] = Cookie(default=None),
) -> dict:
    """FastAPI dependency: require a valid session cookie.
    Use like: def route(user: dict = Depends(get_current_user)): ..."""
    if not saraldoc_session:
        raise HTTPException(status_code=401, detail="Not signed in.")
    try:
        payload = jwt.decode(saraldoc_session, SESSION_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session.")
    return payload


def get_current_user_optional(
    saraldoc_session: Optional[str] = Cookie(default=None),
) -> Optional[dict]:
    """Same as get_current_user but returns None instead of raising, for
    routes that behave differently for signed-in vs anonymous users rather
    than strictly requiring a session."""
    if not saraldoc_session:
        return None
    try:
        return jwt.decode(saraldoc_session, SESSION_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None