import base64
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from flask import Flask, jsonify, request
from greedy_sketch import naive_greedy_sketch, viz
from matplotlib.animation import HTMLWriter
from matplotlib.figure import Figure
from ripser import ripser

logging.basicConfig()

app = Flask(__name__, static_folder="", static_url_path="")


@app.route("/api/animate", methods=["POST"])
def animate():
    app.logger.debug(f"received request {request.json}")
    points = np.array(request.json["points"], dtype=np.double)
    if len(points) == 0:
        raise Exception("points must be non-empty")
    if points.shape[1] != 2:
        raise Exception("expected 2d points int")

    frames = request.json["frames"]
    if type(frames) is not int:
        raise Exception("expected 'frames' as int")

    rips = ripser(points)
    app.logger.debug(f"using rips={rips}")
    if len(rips["dgms"][1]) == 0:
        return "insufficient points"

    fig = Figure()
    ax = fig.add_subplot()
    anim = viz.make_animation(
        naive_greedy_sketch(rips["dgms"][1], minimal=False),
        ax=ax,
    )

    print(anim.to_jshtml())

    return anim.to_html5_video()

    # with TemporaryDirectory() as tmpdir:
    #     path = Path(tmpdir, "temp.html")
    #     writer = HTMLWriter()
    #     anim.save(str(path), writer=writer)
    # return jsonify(writer._saved_frames)


@app.route("/")
def root():
    return app.send_static_file("index.html")
