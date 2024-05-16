from flask import Flask, redirect, render_template, request, url_for, session
from pathlib import Path
from db import db
from models import Customers, Expenses, Shares

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.instance_path = Path('data').resolve()

db.init_app(app)

app.secret_key = 'super'


def get_customer_by_cid(cid):
    return db.session.execute(db.select(Customers).where(Customers.cid == cid)).scalar()


def get_expenses_by_cid(cid):
    return db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid))


def get_expenses_by_cid_and_search(cid, search):
    return db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid).filter(Expenses.name.like('%'+search+'%')))


def get_customer_by_email(email):
    return db.session.query(Customers).filter(Customers.email == email).first()


def get_share_by_joint_id_1(cid):
    return db.session.query(Shares).filter(Shares.joint_id_1 == cid).first()


def get_expense_by_id(id):
    return db.get_or_404(Expenses, id)


def create_expense(name, amount, date, description, cid):
    expense = Expenses(name=name, amount=amount, date=date,
                       description=description, customer_id=cid)
    db.session.add(expense)
    db.session.commit()


def create_customer(email, password, first_name, last_name):
    user = Customers(email=email, password=password,
                     first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()


def delete_expense(expense):
    db.session.delete(expense)
    db.session.commit()


def update_customer(customer):
    db.session.add(customer)
    db.session.commit()


def update_customer_budget(customer, budget, balance, joint="N/A"):
    joint_customer = get_customer_by_email(joint)
    if joint_customer or joint == "N/A":
        customer.joint = joint
    customer.budget = budget
    customer.balance = balance
    db.session.add(customer)
    db.session.commit()


def create_share(customer, joint_customer):
    share = Shares.query.filter_by(joint_id_1=customer.cid).first()

    if not share:
        share = Shares(joint_id_1=customer.cid, joint_id_2=joint_customer.cid)
    else:
        share.joint_id_2 = joint_customer.cid

    customer.budget = joint_customer.budget
    db.session.add(share)
    db.session.commit()


def get_expense_data(cid, search):
    if search is not None:
        return get_expenses_by_cid_and_search(cid, search)
    else:
        return get_expenses_by_cid(cid)


def process_expense_data(data, balance):
    processed_data = []
    before = balance
    for i in data.scalars():
        u = {
            'id': i.eid,
            'name': i.name,
            'amount': i.amount,
            'date': i.date,
            'before': before,
            'balance': before - i.amount
        }
        before -= i.amount
        processed_data.append(u)
    processed_data.reverse()
    return processed_data


def get_budget(customer):
    joint = customer.joint
    if joint != 'None':
        customer_joint = get_customer_by_email(joint)
        return customer_joint.budget if customer_joint else customer.budget
    else:
        return customer.budget


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_customer_by_email(email)
        if user is None or user.password != password:
            return redirect(url_for('login'))
        session['cid'] = user.cid
        return redirect(url_for('expense_homepage'))
    return render_template("login.html")


@app.route("/")
def index():
    return redirect(url_for('login'))


@app.route("/home")
def homepage():
    if 'cid' not in session:
        return redirect(url_for('login'))
    else:
        return render_template("base.html")


@app.route("/submit_form", methods=['POST'])
def submit_form():
    print(request.form.get("search"))
    return redirect(url_for('expense_homepage') + "?search=" + request.form.get("search"))


@app.route("/expenses")
def expense_homepage():
    if 'cid' not in session:
        return redirect(url_for('login'))
    cid = session['cid']
    customer = get_customer_by_cid(cid)
    search = request.args.get("search", None)
    data = get_expense_data(cid, search)
    balance = customer.balance
    processed_data = process_expense_data(data, balance)
    bal_data = get_expenses_by_cid(cid)
    for i in bal_data.scalars():
        balance -= i.amount
    budget = get_budget(customer)
    return render_template("expense.html", transactions=processed_data, balance=balance, joint=customer.joint, budget=budget, search=search)


@app.route("/expenses", methods=['POST'])
def expense_update():
    if 'cid' not in session:
        return redirect(url_for('login'))
    cid = session['cid']
    customer = get_customer_by_cid(cid)
    budget = float(request.form.get("budget") or 0)
    balance = float(request.form.get("balance") or 0)
    joint = request.form.get("joint") or "N/A"
    update_customer_budget(customer, budget, balance, joint)
    joint_customer = get_customer_by_email(joint)

# when users input valid joint_customer, create a share record
    if joint_customer:
        customer.joint = joint
        create_share(customer, joint_customer)
        jsonString = {"message": (
            f"{customer.email} is successfully sharing budget with {joint}")}
# when users leave "joint" box empty, meaning this user doesn't want to share any more, nothing happens to database
    elif joint == "N/A":
        update_customer_budget(customer, budget, balance, joint)
        jsonString = {"message":
                      "You didn't input a joint customer!"}
# when users input content not exiting in database, nothing happen to database
    elif not joint_customer:
        jsonString = {"message":
                      "The joint customer doesn't exit!"}
    return jsonString


@app.route("/expenses/create", methods=['POST'])
def create():
    if 'cid' not in session:
        return redirect(url_for('login'))
    else:
        expense = Expenses(name=request.form.get("name"), amount=request.form.get(
            "amount"), date=request.form.get("date"), description=request.form.get("des"), customer_id=session['cid'] if 'cid' in session else 1)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for("expense_homepage"))


@app.route("/expenses/fillform", methods=['POST', 'GET'])
def fill():
    return render_template('create.html')


@app.route("/expenses/delete/<id>", methods=['POST'])
def expense_delete(id):
    if 'cid' not in session:
        return redirect(url_for('login'))

    expense = db.get_or_404(Expenses, id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if db.session.query(Customers).filter_by(email=email).first():
            return redirect(url_for('register'))
        user = Customers(email=email, password=password,
                         first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route("/settings/fillform")
def set():
    if 'cid' not in session:
        return redirect(url_for('login'))
    customer = db.session.execute(db.select(Customers).where(
        Customers.cid == session['cid'])).scalar()
    return render_template('settings.html', balance=customer.balance, budget=customer.budget, joint=customer.joint)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
