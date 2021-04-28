import base64
import logging
from io import BytesIO

import numpy as np
from flask import Flask, jsonify, request
from greedy_sketch import naive_greedy_sketch, viz
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

    images = []
    for data in anim.new_saved_frame_seq():
        anim._draw_next_frame(data, blit=False)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Must decode bytes to ensure that it gets added to string correctly
        encoded = base64.encodebytes(buf.getvalue()).decode("ascii")
        images.append(f"data:image/png;base64,{encoded}")

    return jsonify(images)


@app.route("/")
def root():
    return app.send_static_file("index.html")
