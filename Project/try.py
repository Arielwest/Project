from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def foo():
    if request.method == 'POST':
        print request.form.getlist('check')
    return render_template('try.html')


if __name__ == "__main__":
    app.run(host='localhost', port=8888, debug=True)
