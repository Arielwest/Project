import os
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def dirtree():
    return render_template('try.html')


if __name__ == "__main__":
    app.run(host='localhost', port=8888, debug=True)
