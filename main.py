
from flask import Flask, redirect, render_template, request, url_for
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
    balance = 1000
    for i in data.scalars():
        u = {
            'id': i.id,
            'name': i.name,
            'amount': i.amount,
            'date': i.date,
            # 'description': i.description if i.description else 'N/A',
            'before': balance,
            'balance': balance - i.amount
        }
        balance -= i.amount
        processed_data.append(u)
        # print(data)
    processed_data.reverse()
    return render_template("base.html", transactions=processed_data, balance=balance)
    # return render_template("base.html")


@app.route("/create", methods=['GET', 'POST'])
def create():
    expense = Expenses(name=request.form.get("name"), amount=request.form.get(
        "amount"), date=request.form.get("date"), description=request.form.get("des"))
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("homepage"))


@app.route("/fillform", methods=['POST'])
def fill():
    return render_template('create.html')

@app.route("/delete/name", methods=['POST'])
def delete(name):
    expense = db.get_or_404(Expenses, name)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for("homepage"))



if __name__ == '__main__':
    app.run(debug=True, port=3000)
