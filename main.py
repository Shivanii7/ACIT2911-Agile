from flask import Flask, jsonify, request, render_template
from pathlib import Path
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.instance_path = Path('data').resolve()

db.init_app(app)

@app.route("/<a>")
def hello(a):
    try: 
        a = a.replace("%20", " ")
        return f"Hello {a}!"
    except:
        return "Hello World!"

@app.route("/")
def homepage():
    return render_template("base.html")



if __name__ == '__main__':
    app.run(debug=True, port=3000)
