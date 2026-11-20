
from flask import Blueprint, g, jsonify

api = Blueprint("api", __name__)


@api.get("/api/data")
def data():
    state = getattr(g, "rl", None)
    return jsonify(
        message="Request successful",
        remaining=state["remaining"] if state else None,
    )


@api.get("/health")
def health():
    return jsonify(status="ok")
