

import logging
import math
from datetime import datetime, timezone

from flask import g, jsonify, request
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .config import FAIL_OPEN, LIMIT, WINDOW_SECONDS
from .db import rate_limit

log = logging.getLogger("ratelimiter")
EXEMPT_PATHS = {"/health"}


def identify_client():
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key}"
    return f"ip:{request.remote_addr}"


def check_rate_limit(client_id):
    """Atomically register one request and return the limiter state."""
    window_ms = WINDOW_SECONDS * 1000


    new_window = {
        "$or": [
            {"$eq": [{"$type": "$windowStart"}, "missing"]},
            {"$lte": [{"$add": ["$windowStart", window_ms]}, "$$NOW"]},
        ]
    }
    pipeline = [
        {
            "$set": {
                "windowStart": {"$cond": [new_window, "$$NOW", "$windowStart"]},
                "requestCount": {
                    "$cond": [
                        new_window,
                        1,
                        {"$min": [{"$add": ["$requestCount", 1]}, LIMIT + 1]},
                    ]
                },
            }
        },
        {"$set": {"expiresAt": {"$add": ["$windowStart", window_ms]}}},
    ]

    def run():
        return rate_limit.find_one_and_update(
            {"clientId": client_id},
            pipeline,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    try:
        doc = run()
    except DuplicateKeyError:
        doc = run()

    now = datetime.now(timezone.utc)
    reset_in = max(0, math.ceil((doc["expiresAt"] - now).total_seconds()))
    count = doc["requestCount"]
    return {
        "allowed": count <= LIMIT,
        "remaining": max(0, LIMIT - count),
        "reset_in": reset_in,
    }


def register_rate_limiter(app):
    @app.before_request
    def enforce_rate_limit():
        if request.path in EXEMPT_PATHS:
            return None
        try:
            state = check_rate_limit(identify_client())
        except PyMongoError as exc:
            log.error("Rate limiter DB error: %s", exc)
            if FAIL_OPEN:
                return None
            return jsonify(error="Rate limiter unavailable"), 503

        g.rl = state
        if not state["allowed"]:
            resp = jsonify(
                error="Too Many Requests",
                message=f"Limit of {LIMIT} requests per {WINDOW_SECONDS}s exceeded.",
                retry_after_seconds=state["reset_in"],
            )
            resp.status_code = 429
            resp.headers["Retry-After"] = str(state["reset_in"])
            return resp
        return None

    @app.after_request
    def add_rate_limit_headers(resp):
        state = getattr(g, "rl", None)
        if state:
            resp.headers["X-RateLimit-Limit"] = str(LIMIT)
            resp.headers["X-RateLimit-Remaining"] = str(state["remaining"])
            resp.headers["X-RateLimit-Reset"] = str(state["reset_in"])
        return resp
