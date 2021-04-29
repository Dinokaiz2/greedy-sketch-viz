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
    points = np.array(request.json, dtype=np.double)
    if len(points) == 0:
        raise Exception("points must be non-empty")
    if points.shape[1] != 2:
        raise Exception("expected 2d points int")

    rips = ripser(points)
    app.logger.debug(f"using rips={rips}")
    if len(rips["dgms"][1]) == 0:
        return "insufficient points"

    fig = Figure()
    ax = fig.add_subplot()
    anim = viz.make_greedy_sketch_animation(
        naive_greedy_sketch(rips["dgms"][1], minimal=False),
        ax=ax,
    )

    # Ideally, we'd just return `anim.to_jshtml()`. However, for that to work
    # it has <script> tags inside of the HTML, so if the client were to just
    # shove those into a DOM node, they wouldn't get executed for security. We
    # could `eval()` them but that is really gross, insecure, and also had a
    # ton of errors when I tried.
    #
    # Instead, our webpage has a duplicate of the animation HTML and Javscript
    # itself and the server just returns the frames of the animation in the way
    # that JS expects. However, matplotlib.animation provides no easy way to
    # inspect individual frames of the animation without hitting the
    # filesystem. Instead, it prefers you to save files in a specific format
    # (e.g. gif, mp4), so we have to manually call the private
    # `Animation._draw_next_frame()` to draw the frame and then save that to a
    # PNG in memory.
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
