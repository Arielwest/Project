from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def foo():
    return render_template("foo.html")

if __name__ == "__main__":
    app.run()
