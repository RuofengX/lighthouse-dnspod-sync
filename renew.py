import threading
import time
import urllib.request
from pprint import pprint as print
import json
import os

import typer
import uvicorn

from server import app


def main(instance_name: str) -> None:
    server = threading.Thread(
        target=uvicorn.run, kwargs={"app": app, "host": "127.0.0.1", "port": 60008}
    )
    server.start()

    time.sleep(1)
    print("start...")
    with urllib.request.urlopen(f"http://127.0.0.1:60008/renew/{instance_name}") as f:
        result = f.read().decode("utf-8")

    print(json.loads(result))
    print("Done!")
    print("You can use ^C to exit.")


if __name__ == "__main__":
    typer.run(main)
