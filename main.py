
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
    if 'cid' not in session:
        return redirect(url_for('login'))

    cid = session['cid']

    customer = db.session.execute(
        db.select(Customers).where(Customers.cid == cid)).scalar()
    data = db.session.execute(
        db.select(Expenses).filter(Expenses.customer_id == cid))
    processed_data = []

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
    if joint != 'None':
        customer_joint = db.session.query(Customers).filter(
            Customers.email == joint).first()
        if not customer_joint:
            budget = customer.budget
        else:
            budget = customer_joint.budget
    else:
        budget = customer.budget

    return render_template("expense.html", transactions=processed_data, balance=balance, joint=joint, budget=budget)


@app.route("/expenses", methods=['POST'])
def expense_homepage():
    if 'cid' not in session:
        return redirect(url_for('login'))
    cid = session['cid']

    customer = db.session.execute(
        db.select(Customers).where(Customers.cid == cid)).scalar()

    data = db.session.execute(
        db.select(Expenses).filter(Expenses.customer_id == cid))

    budget = float(request.form.get("budget", 0))
    balance = float(request.form.get("balance", 0))
    joint = request.form.get("joint")

    customer.budget = budget
    customer.balance = balance
    customer.joint = joint
    # # print(customer.to_json())
    db.session.add(customer)
    db.session.commit()

    joint_customer = db.session.query(Customers).filter(
        Customers.email == joint).first()
    print(joint_customer)
# when users input valid joint_customer, create a share record
    if joint_customer:
        customer.joint = joint
        share = db.session.query(Shares).filter(
            Shares.joint_id_1 == cid).first()
        # if the logged customer doesn't exit in the share table as joint_id_1, then create
        if not share:
            share = Shares(joint_id_1=cid, joint_id_2=joint_customer.cid)
            # if the logged customer exits in the share table as joint_id_1, then update
        else:
            share = db.session.execute(
                db.select(Shares).where(Shares.joint_id_1 == cid)).scalar()
            share.joint_id_2 = joint_customer.cid
        customer.budget = joint_customer.budget
        db.session.add(share)
        db.session.commit()
        return render_template("message_share.html", option=1, customer_current=customer.email, customer_joint=joint)
# when users leave "joint" box empty, meaning this user doesn't want to share any more, balance and budget will be updated in database
    elif joint == "N/A":
        print("budget", budget)
        print("budgetc", customer.budget)
        customer.budget = budget
        customer.balance = balance
        customer.joint = joint
        db.session.add(customer)
        db.session.commit()
        return render_template("message_share.html", option=2, customer_current=customer.email, customer_joint=joint)
# when users input content not exiting in database, nothing happen to database
    elif not joint_customer:
        return render_template("message_share.html", option=0, customer_current=customer.email, customer_joint=joint)


@app.route("/expenses/create", methods=['POST'])
def create():
    expense = Expenses(name=request.form.get("name"), amount=request.form.get(
        "amount"), date=request.form.get("date"), description=request.form.get("des"), customer_id=session['cid'] if 'cid' in session else 1)
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
        if user is None:
            return redirect(url_for('login'))
        if user.password == password:
            session['cid'] = user.cid
            # print(session['cid'])
            return redirect(url_for('homepage'))
        return redirect(url_for('login'))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route("/settings/fillform")
def set():
    # auto fill form with previous data
    # do it later
    customer = db.session.execute(db.select(Customers).where(
        Customers.cid == session['cid'])).scalar()
    print(customer.balance)
    print(customer.budget)
    return render_template('settings.html', balance=customer.balance, budget=customer.budget, joint=customer.joint)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
