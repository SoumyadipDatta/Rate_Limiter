
from rate_limiter import create_app
from rate_limiter.config import PORT
from rate_limiter.db import init_indexes

app = create_app()

if __name__ == "__main__":
    init_indexes()
    app.run(host="0.0.0.0", port=PORT)
