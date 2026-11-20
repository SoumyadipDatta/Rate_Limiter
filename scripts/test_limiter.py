
import json
import sys
import urllib.error
import urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/api/data"

for i in range(1, 8):
    req = urllib.request.Request(URL, headers={"X-API-Key": "user123"})
    try:
        with urllib.request.urlopen(req) as r:
            status, headers, body = r.status, r.headers, json.load(r)
    except urllib.error.HTTPError as e:
        status, headers, body = e.code, e.headers, json.load(e)
    print(f"#{i}: {status} remaining={headers.get('X-RateLimit-Remaining')} "
          f"retry_after={headers.get('Retry-After')} -> {body.get('message') or body.get('error')}")
