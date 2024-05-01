from flask import Flask
from pathlib import Path
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.instance_path = Path('data').resolve()

db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
