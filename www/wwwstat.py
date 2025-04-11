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
    return redirect(url_for("static", filename="static.html"), code=302)



@app.route("/histo/", methods=['GET'])
def histo():
    return render_template("histo.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5001 )

