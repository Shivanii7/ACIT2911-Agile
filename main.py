
from flask import Flask, redirect, render_template, request, url_for, session
from pathlib import Path
from db import db
from models import Customers, Expenses, Shares
from models import Expenses, Customers

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.instance_path = Path('data').resolve()

db.init_app(app)

app.secret_key = 'super'


@app.route("/")
def index():
    if 'cid' in session:
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login'))


@app.route("/home")
def homepage():
    return render_template("base.html")


@app.route("/expenses", methods=['GET'])
def expense_homepage_get():
    data = db.session.execute(db.select(Expenses))
    processed_data = []
    # ============!!!!!!!!!!!!!!!hardcode cid: change after authentication

    customer = db.session.execute(
        db.select(Customers).where(Customers.cid == 1)).scalar()
    balance = customer.balance
    for i in data.scalars():
        u = {
            'id': i.eid,
            'name': i.name,
            'amount': i.amount,
            'date': i.date,
            'before': balance,
            'balance': balance - i.amount
        }
        balance -= i.amount
        processed_data.append(u)
    processed_data.reverse()
    joint = customer.joint
    # share = db.session.query(Shares).filter(Shares.joint_id_1 == 1).first()
    if joint != 'None':
        print(1)
        customer_joint = db.session.query(Customers).filter(
            Customers.email == joint).first()
        print(customer_joint)
        print("budget", customer_joint.budget)
        if not customer_joint:
            budget = customer.budget
        else:
            budget = customer_joint.budget
        print("budget", budget)
    else:
        budget = customer.budget

    return render_template("expense.html", transactions=processed_data, balance=balance, joint=joint, budget=budget)


@app.route("/expenses", methods=['POST'])
def expense_homepage():
    # data = db.session.execute(db.select(Expenses))
    # processed_data = []
    budget = float(request.form.get("budget") or 0)
    balance = float(request.form.get("balance") or 0)
    joint = request.form.get("joint") or "None"
    # ============!!!!!!!!!!!!!!!hardcode cid: change after authentication

    if joint != "None":
        print(2)
        share = db.session.query(Shares).filter(Shares.joint_id_1 == 1).first()
        print(joint)
        if not share:
            share = Shares(joint_id_1=1, joint_id_2=joint)
        else:
            share = db.session.execute(
                db.select(Shares).where(Shares.joint_id_1 == 1)).scalar()

        db.session.add(share)
    customer = db.session.execute(
        db.select(Customers).where(Customers.cid == 1)).scalar()
    print(customer.to_json())
    customer.budget = budget
    customer.balance = balance
    customer.joint = joint
    # print(customer.to_json())
    db.session.add(customer)
    db.session.commit()

    return f"{customer.email} has shared target with {joint}"


@app.route("/expenses/create", methods=['POST'])
def create():
    expense = Expenses(name=request.form.get("name"), amount=request.form.get(
        "amount"), date=request.form.get("date"), description=request.form.get("des"))
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage_get"))


@app.route("/expenses/fillform", methods=['POST'])
def fill():
    return render_template('create.html')


@app.route("/expenses/delete/<id>", methods=['POST'])
def expense_delete(id):
    expense = db.get_or_404(Expenses, id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for("homepage"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user = Customers(email=email, password=password,
                         first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.session.query(Customers).filter_by(email=email).first()
        if user.password == password:
            return redirect(url_for('homepage'))
        return redirect(url_for('login'))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route("/settings/fillform")
def set():
    return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True, port=3000)
