#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, redirect,flash
from flask import jsonify
from json import dumps

app = Flask(__name__,) 

from os import path


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data/", methods=['GET'])
def data():
    return redirect(url_for('static', filename="data.json"))


@app.route("/histo/", methods=['GET'])
def histo():
    return render_template("histo.html")

@app.route("/status/", methods=['GET'])
def status():
    return render_template("status.html")

@app.route("/time/", methods=['GET'])
def time():
    return render_template("time.html")

@app.route("/core/", methods=['GET'])
def core():
    return render_template("core.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5001 )

