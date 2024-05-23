from datetime import datetime
from turtle import up
from turtle import up
from unicodedata import category
from flask import Flask, flash, redirect, render_template, request, url_for, session
from pathlib import Path
from flask.config import T
from db import db
from models import Customers, Expenses, Shares

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.instance_path = Path('data').resolve()

db.init_app(app)

app.secret_key = 'super'


def get_customer_by_cid(cid):
    return db.session.execute(db.select(Customers).where(Customers.cid == cid)).scalar() or None


def get_expenses_by_cid(cid):
    return db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid)) or None


def get_expenses_by_cid_and_month(cid, month_str):
    return db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid).filter(Expenses.date.like('%'+'-'+month_str+'-'+'%'))) or None


def get_expenses_by_cid_and_search(cid, search):
    return db.session.execute(db.select(Expenses).filter(Expenses.customer_id == cid).filter(Expenses.name.like('%'+search+'%'))) or None


def get_customer_by_email(email):
    return db.session.query(Customers).filter(Customers.email == email).first() or None


def get_share_by_joint_id_1(cid):
    return db.session.query(Shares).filter(Shares.joint_id_1 == cid).first() or None

def get_expense_by_id(id):
    return db.get_or_404(Expenses, id) or None


def create_expense(name, amount, date, transaction_category, cid):
    expense = Expenses(name=name, amount=amount, date=date, transaction_category=transaction_category, customer_id=cid)
    db.session.add(expense)
    db.session.commit()


def create_customer(email, password, first_name, last_name):
    user = Customers(email=email, password=password, first_name=first_name, last_name=last_name)
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
    if joint_customer:
        customer.joint = joint
        customer.budget = joint_customer.budget
    elif budget:
        customer.budget = budget
        customer.joint = "N/A"

    if balance:
        customer.balance = balance

    db.session.add(customer)
    db.session.commit()


def create_share(customer, joint_customer):
    if customer and joint_customer:
        share = Shares.query.filter_by(joint_id_1=customer.cid).first()
    else:
        share = None

    if share:
        share = Shares(joint_id_1=customer.cid, joint_id_2=joint_customer.cid)
        customer.budget = joint_customer.budget
        db.session.add(share)
    else:
        share = share

    db.session.commit()

def get_transaction_by_id(transaction_id):
    transaction = db.session.execute(db.select(Expenses).where(Expenses.eid == transaction_id)).scalar()
    return transaction

def update_transaction(transaction_id, name, date, amount, transaction_category):
    transaction = get_transaction_by_id(transaction_id)
    if transaction is None:
        print(f"No transaction found with id {transaction_id}")
        return
    transaction.name = name
    transaction.date = date
    transaction.amount = amount
    transaction.transaction_category = transaction_category
    db.session.commit()

def get_expense_data(cid, search):
    if search is not None:
        return get_expenses_by_cid_and_search(cid, search)
    else:
        return get_expenses_by_cid(cid)


# def process_expense_data(data, balance):
#     processed_data = []
#     before = balance
    
#     if isinstance(data, dict):
#         u = {
#             'id': data["eid"],
#             'name': data["name"],
#             'amount': data["amount"],
#             'date': data["date"],
#             'before': before,
#             'balance': before - data["amount"]
#         }
#         before -= data["amount"]
#         processed_data.append(u)
#     else:
#         for i in data.scalars():
#             u = {
#                 'id': i.eid,
#                 'name': i.name,
#                 'amount': i.amount,
#                 'date': i.date,
#                 'before': before,
#                 'balance': before - i.amount
#             }
#             before -= i.amount
#             processed_data.append(u)

#     processed_data.reverse()
#     return processed_data

def process_expense_data(data, balance):
    processed_data = []
    before = balance
    
    if isinstance(data, dict):
        if data["transaction_category"] == "income":
            balance += data["amount"]
        elif data["transaction_category"] == "expense":
            balance -= data["amount"]
        u = {
            'id': data["eid"],
            'name': data["name"],
            'transaction_category': data["transaction_category"], 
            'amount': data["amount"],
            'date': data["date"],
            'before': before,
            'balance': balance
        }
        before = balance
        processed_data.append(u)
    else:
        for i in data.scalars():
            if i.transaction_category == "income":
                balance += i.amount
            elif i.transaction_category == "expense":
                balance -= i.amount
            u = {
                'id': i.eid,
                'name': i.name,
                'amount': i.amount,
                'transaction_category': i.transaction_category,
                'date': i.date,
                'before': before,
                'balance': balance
            }
            before = balance
            processed_data.append(u)

    processed_data.reverse()
    return processed_data

# def get_budget(customer):
#     joint = customer.joint
#     if joint != None:
#         customer_joint = get_customer_by_email(joint)
#         return customer_joint.budget if customer_joint else customer.budget
#     else:
#         return customer.budget

def balance_update(balance, bal_data):
    total_spent = 0
    for i in bal_data.scalars():
        total_spent += i.amount
        balance -= i.amount
    return [balance, total_spent]

def update_spent(customer, spent):
    customer.spent = spent
    db.session.add(customer)
    db.session.commit()

def convert_month(month):
    if month % 10 == month:
        month_str = '0'+str(month)
    else:
        month_str = str(month)
    return month_str

# validation functions

def validate_name(name):
    if not name or not isinstance(name, str):
        # flash("Invalid name.")
        return False
    return True

def validate_amount(amount):
    try:
        return float(amount)
    except (ValueError, TypeError):
        # flash("Invalid amount.")
        return None

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
    return redirect(url_for('expense_homepage') + "?search=" + request.form.get("search"))


@app.route("/expenses/month_form", methods=['POST'])
def accept_month():
    if 'cid' not in session:
        return redirect(url_for('login'))
    cid = session['cid']
    if not request.form.get("months"):
        date = datetime.today()
        month = date.month
    else:
        month = int(request.form.get("months"))
    month_str = convert_month(month)
    expenses_month = get_expenses_by_cid_and_month(cid, month_str)
    month_spent = 0
    for i in expenses_month.scalars():
        month_spent += i.amount
    session['month_spent'] = month_spent
    session['month_int'] = month
    return redirect(url_for('expense_homepage'))


@app.route("/expenses", methods=['GET'])
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
    current_month = datetime.today().month
    current_month_str = convert_month(current_month)
    expenses_current_month = get_expenses_by_cid_and_month(
        cid, current_month_str)
    current_month_spent = 0
    for i in expenses_current_month.scalars():
        current_month_spent += i.amount
    for i in bal_data.scalars():
        balance -= i.amount
    update_spent(customer, current_month_spent)
    budget = customer.budget
    month_spent = session.get('month_spent', 0)
    month = session.get('month_int', 0)
    value = budget-current_month_spent
    return render_template("expense.html", value=value, transactions=processed_data, month_spent=month_spent, spent=current_month_spent, balance=balance, joint=customer.joint, budget=budget, search=search, month=month)


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
    elif not joint and not balance and not budget:
        jsonString = {"message": "Your status doesn't change!"}
    else:
        jsonString = {
            "message": "Set successfully! You are not sharing budget with others!"}

# # when users leave "joint" box empty, joint status doesn't change
#     elif joint == "N/A" and budget:
#         jsonString = {"message": (
#             f"{customer.email} is successfully sharing budget with {joint}")}
#         update_customer_budget(customer, budget, balance, joint)
#         jsonString = {"message":
#                       "Your sharing status doesn't change!"}
# # when users input content not exiting in database, nothing happen to database
#     elif not joint_customer:
#         jsonString = {"message":
#                       "The joint customer doesn't exit!"}
    return jsonString


@app.route("/expenses/create", methods=['POST'])
def create():
    if 'cid' not in session:
        return redirect(url_for('login'))
    name = request.form.get("name")
    amount = request.form.get("amount")
    date = request.form.get("date")
    transaction_category = request.form.get("transaction_category")
    customer_id = session['cid'] if 'cid' in session else 1

    if not validate_name(name):
        return redirect(url_for("expense_homepage"))

    amount = validate_amount(amount)
    if amount is None:
        return redirect(url_for("expense_homepage"))

    expense = Expenses(name=name, amount=amount, date=date, transaction_category=transaction_category, customer_id=customer_id)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage"))


@app.route("/expenses/fillform", methods=['POST', 'GET'])
def fill():
    return render_template('create.html')

@app.route('/edit_form')
def edit_form():
    transaction_id = request.args.get('id')
    #print(f"Transaction ID: {transaction_id}")
    transaction = get_transaction_by_id(transaction_id) 
    return render_template('edit_form.html', transaction=transaction)

@app.route('/edit_transaction', methods=['POST'])
def edit_transaction():
    form_data = request.form
    print(f"Form data: {form_data}")  
    transaction_id = form_data.get('id')
    transaction = get_transaction_by_id(transaction_id)

    transaction.name = form_data.get('name')
    transaction.date = form_data.get('date')
    transaction.amount = form_data.get('amount')

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing transaction: {e}")
        return "Error: Could not save changes"

    return redirect(url_for('expense_homepage'))

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
        user = Customers(email=email, password=password, first_name=first_name, last_name=last_name)
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


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True, port=3000)  # pragma: no cover
