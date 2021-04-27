import logging

from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="", static_url_path="")


@app.route("/api/points", methods=["POST"])
def ping():
    points = request.json
    logging.info(points)
    for x, y in points:
        if type(x) is not int and type(x) is not float:
            raise Exception("unexpected type of x")
        if type(y) is not int and type(y) is not float:
            raise Exception("unexpected type of y")

    return jsonify(points)


@app.route("/")
def root():
    return app.send_static_file("index.html")
