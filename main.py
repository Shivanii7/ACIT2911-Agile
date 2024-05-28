from datetime import datetime
from turtle import up
from turtle import up
from unicodedata import category
from flask import Flask, flash, redirect, render_template, request, url_for, session
from werkzeug.utils import secure_filename
from pathlib import Path
from db import db
from models import Customers, Expenses, Shares
from flask_bcrypt import Bcrypt
from werkzeug.datastructures import FileStorage
import os

def create_app(testing=False):
    app = Flask(__name__)
    app.secret_key = 'super'
    if testing:
        # In-memory database for testing
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        app.instance_path = Path("./data").resolve()
    else:
        # Main database URI
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
        app.instance_path = Path("./data").resolve()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)
    return app


app = create_app()
bcrypt = Bcrypt(app)

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


UPLOAD_FOLDER = 'static/receipt_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_receipt_image(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            print(f"File saved successfully at {file_path}")
            return file_path
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    return None

# def create_expense(name, amount, date, transaction_category, cid, receipt_image_path):
#     if 'receipt_image' in request.files:
#         receipt_image = request.files['receipt_image']
#         receipt_image_path = save_receipt_image(receipt_image)
#     # receipt_image = request.files['receipt_image']
#     # receipt_image_path = save_receipt_image(receipt_image)  
#     else:
#         receipt_image_path = None
#     expense = Expenses(name=name, amount=amount, date=date, transaction_category=transaction_category, customer_id=cid, receipt_image_path=receipt_image_path)
#     db.session.add(expense)
#     db.session.commit()

def create_expense(name, amount, date, transaction_category, cid, receipt_image_data=None):
    if receipt_image_data:
        if isinstance(receipt_image_data, FileStorage):
            receipt_image_path = save_receipt_image(receipt_image_data)
        else:
            print(f"Error: receipt_image_data is not a FileStorage object")
            return
    else:
        receipt_image_path = None    
    expense = Expenses(name=name, amount=amount, date=date, transaction_category=transaction_category, customer_id=cid, receipt_image_path=receipt_image_path)
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
    transaction = db.session.query(Expenses).filter(Expenses.eid == transaction_id).first()
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
            'balance': balance,
            'receipt_image_path': data["receipt_image_path"] if "receipt_image_path" in data else None
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
                'balance': balance,
                'receipt_image_path': i.receipt_image_path if i.receipt_image_path else None
            }
            before = balance
            processed_data.append(u)

    processed_data.reverse()
    return processed_data

def balance_update(balance, bal_data):
    total_spent = 0
    for i in bal_data.scalars():
        if i.transaction_category == "expense":
            balance -= i.amount
            total_spent += i.amount  
        elif i.transaction_category == "income":
            balance += i.amount
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


def validate_name(name):
    if not name or not isinstance(name, str):
        return False
    return True


def validate_amount(amount):
    try:
        return float(amount)
    except (ValueError, TypeError):
        return None
    
def update_current_month_spent(cid, current_month_str):
    print(cid, current_month_str)
    x = get_expenses_by_cid_and_month(cid, current_month_str)
    current_month_spent = 0
    for i in x.scalars():
        if i.transaction_category == "expense":
            current_month_spent += i.amount 
        else:
            current_month_spent -= i.amount
    return current_month_spent
        
def get_current_month_spent(cid):
    current_month = datetime.today().month
    current_month_str = convert_month(current_month)
    expenses_current_month = get_expenses_by_cid_and_month(
        cid, current_month_str)
    current_month_spent = update_current_month_spent(cid, current_month_str)
    return current_month_spent

def update_balance(cid,balance):
    bal_data = get_expenses_by_cid(cid)
    for i in bal_data.scalars():
        balance -= i.amount
 
def update_current_month_spent_expense(cid, current_month_str):
    x = get_expenses_by_cid_and_month(cid, current_month_str)
    current_month_spent = 0
    for i in x.scalars():
        if i.transaction_category == "expense":
            current_month_spent += i.amount 
    return current_month_spent

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_customer_by_email(email)

        if user and bcrypt.check_password_hash(user.password, password):
            session['cid'] = user.cid
            return redirect(url_for('homepage'))
        
        else:
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/home")
def homepage():
    if 'cid' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('expense_homepage')) 

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
    print("str",month_str)
    expenses_month = get_expenses_by_cid_and_month(cid, month_str)
    month_spent = 0
    month_earned = 0
    for i in expenses_month.scalars():
        month_spent += i.amount if i.transaction_category == "expense" else 0
        month_earned += i.amount if i.transaction_category == "income" else 0
    session['month_spent'] = month_spent
    session['month_int'] = month
    session['month_earned'] = month_earned
    return redirect(url_for('expense_homepage')+'?month=' + month_str)

@app.route("/expenses", methods=['GET'])
def expense_homepage():
    if 'cid' not in session:
        return redirect(url_for('login'))
    cid = session['cid']
    customer = get_customer_by_cid(cid)
    balance = customer.balance   
    budget = customer.budget
    
    search = request.args.get("search", None)
    month_str=request.args.get("month", None)
    print(month_str)
    if search:
        data = get_expense_data(cid, search) 
    elif month_str:
        data = get_expenses_by_cid_and_month(cid, month_str) 
    else:
        data = get_expense_data(cid,None)
    processed_data = process_expense_data(data, balance)
    bal_data = get_expenses_by_cid(cid)
    current_month = datetime.today().month
    current_month_str = convert_month(current_month)
    expenses_current_month = get_expenses_by_cid_and_month(cid, current_month_str)
    current_month_spent = update_current_month_spent_expense(cid, current_month_str)
    # for i in expenses_current_month.scalars():
    #     current_month_spent += i.amount if i.transaction_category == "expense" else 0
    
    balance = balance_update(balance, bal_data)[0]
    update_spent(customer, current_month_spent)
    budget = customer.budget
   
    current_month_spent=get_current_month_spent(cid)
    update_spent(customer, current_month_spent)    
 
    update_balance(cid,balance)
  
    month_spent = session.get('month_spent', 0)
    month_earned = session.get('month_earned', 0)
    month = session.get('month_int', 0)
    value = budget-current_month_spent
    return render_template("expense.html", value=value, transactions=processed_data, month_spent=month_spent, spent=current_month_spent, balance=balance, joint=customer.joint, budget=budget, search=search, month=month, month_earned=month_earned)

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
    name_list= db.session.execute(db.select(Customers.email)).scalars()
    if joint_customer:
        customer.joint = joint
        create_share(customer, joint_customer)
        jsonString = {"message": (
            f"{customer.email} is successfully sharing budget with {joint}"),"redirect_url": url_for('expense_homepage')}
    elif joint=='N/A' and not balance and not budget:
        jsonString = {"message": "Your status doesn't change!","redirect_url": url_for('expense_homepage')}
    elif joint=='N/A' and (balance or budget):
        jsonString = {"message": "Set successfully! You are not sharing budget with others!","redirect_url": url_for('expense_homepage')}
    elif joint is not None and (joint not in name_list):
        jsonString = {"message": "You input non-existing cusotmer!","redirect_url": url_for('expense_homepage')}
    else:
        jsonString = {
            "message": "Set successfully!","redirect_url": url_for('expense_homepage')}
    print(jsonString['redirect_url'])
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
    receipt_image = request.files.get("receipt_image")
    receipt_image_path = save_receipt_image(receipt_image)
    if not receipt_image:
        receipt_image_path = None    

    if not validate_name(name):
        flash("Invalid name.")
        return redirect(url_for("expense_homepage"))

    amount = validate_amount(amount)
    if amount is None:
        flash("Invalid amount.")
        return redirect(url_for("expense_homepage"))

    expense = Expenses(name=name, amount=amount, date=date, transaction_category=transaction_category, customer_id=customer_id, receipt_image_path=receipt_image_path)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("expense_homepage"))


@app.route("/expenses/fillform", methods=['POST', 'GET'])
def fill():
    return render_template('create.html')


@app.route('/edit_form')
def edit_form():
    transaction_id = request.args.get('id')
    transaction = get_transaction_by_id(transaction_id)
    return render_template('edit_form.html', transaction=transaction)


@app.route('/edit_transaction', methods=['POST'])
def edit_transaction():
    form_data = request.form
    print(f"Form data: {form_data}")  
    transaction_id = form_data.get('id')
    transaction = get_transaction_by_id(transaction_id)

    amount = form_data.get('amount')
    try:
        amount = float(amount)
    except ValueError:
        flash("Invalid amount")
        return redirect(url_for('expense_homepage'))

    transaction.name = form_data.get('name')
    transaction.date = form_data.get('date')
    transaction.amount = form_data.get('amount')
    transaction.transaction_category = form_data.get('transaction_category')
    receipt_image = request.files.get('receipt_image')

    if receipt_image:
        receipt_image_path = save_receipt_image(receipt_image)
        if receipt_image_path:
            transaction.receipt_image_path = receipt_image_path
        else:
            print("Error saving receipt image")

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
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if db.session.query(Customers).filter_by(email=email).first():
            return redirect(url_for('register'))
        user = Customers(email=email, password=hashed_password, first_name=first_name, last_name=last_name)
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
