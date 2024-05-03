from flask import Flask, jsonify, request, render_template
from pathlib import Path
from db import db
from models import Expenses

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.instance_path = Path('data').resolve()

db.init_app(app)

@app.route("/")
def homepage():
    data = db.session.execute(db.select(Expenses))
    processed_data = []
    for i in data.scalars():
        u = {
            'id': i.id,
            'name': i.name,
            'amount': i.amount,
            'date': i.date,
            # 'description': i.description if i.description else 'N/A',
            'balance': 'N/A'
        }
        processed_data.append(u)
        # print(data)
        
    return render_template("base.html", transactions=processed_data)
    # return render_template("base.html")

if __name__ == '__main__':
    app.run(debug=True, port=3000)
