
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
    # # --------------------------
    # id = 1
    # shares = db.session.execute(db.select(Shares))
    # for i in shares.scalars():
    #     if id in i.joint_id_1:
    #         customer = db.session.execute(
    #             db.select(Customers).where(Customers.cid == i.joint_id_2))
    # # --------------------------
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
            # 'description': i.description if i.description else 'N/A',
            'before': balance,
            'balance': balance - i.amount
        }
        balance -= i.amount
        processed_data.append(u)
    # print(data)
    processed_data.reverse()
    budget = customer.budget
    joint = customer.joint

    return render_template("expense.html", transactions=processed_data, balance=balance, joint=joint, budget=budget)


@app.route("/expenses", methods=['POST'])
def expense_homepage():
    data = db.session.execute(db.select(Expenses))
    processed_data = []
    budget = float(request.form.get("budget", 0))
    balance = float(request.form.get("balance", 0))
    joint = request.form.get("joint")
    # ============!!!!!!!!!!!!!!!hardcode cid: change after authentication

    customer = db.session.execute(
        db.select(Customers).where(Customers.cid == 1)).scalar()
    # print(customer.to_json())
    customer.budget = budget
    customer.balance = balance      
    customer.joint = joint
    # print(customer.to_json())
    db.session.add(customer)
    db.session.commit()

    for i in data.scalars():
        u = {
            'id': i.eid,
            'name': i.name,
            'amount': i.amount,
            'date': i.date,
            # 'description': i.description if i.description else 'N/A',
            'before': customer.balance,
            'balance': customer.balance - i.amount
        }
        customer.balance -= i.amount
        processed_data.append(u)
        # print(data)
    processed_data.reverse()

    return render_template("expense.html", transactions=processed_data, balance=customer.balance, joint=customer.joint, budget=customer.budget)


@app.route("/expenses/create", methods=['POST'])
def create():
    expense = Expenses(name=request.form.get("name"), amount=request.form.get(
        "amount"), date=request.form.get("date"), description=request.form.get("des"), customer_id = request.form.get("cid"))
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage_get"))


@app.route("/expenses/fillform", methods=['POST'])
def fill():
    return render_template('create.html')


@app.route("/expenses/delete/<id>", methods=['POST'])
def expense_delete(id):
    data = db.session.execute(db.select(Expenses))
    if data:
        for i in data.scalars():
            print(i.eid)
            
    expense = db.get_or_404(Expenses, id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage_get"))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user = Customers(email=email, password=password, first_name=first_name, last_name=last_name)
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
        if user is None:
            return redirect(url_for('login'))
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
