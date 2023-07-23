import json
from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_marshmallow import Marshmallow
from datetime import datetime
import uuid

class FlaskJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, YourFlaskCustomObject):
            # Serialize your custom Flask object here
            return obj.to_json()
        return super().default(obj)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '199606@199606'  # Change this to your preferred secret key
app.json_encoder = FlaskJSONEncoder  # Specify the JSONEncoder class


db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)

api = Api(app, version='1.0', title='FinTrack API - Empowering Efficient Financial Tracking and Management.',
          description='Empower Efficient Financial Tracking and Management. Seamlessly handle transactions, track expenses & incomes, manage customers and suppliers, manage invoices, calculate specific period revenue and gain enhanced control over your financial data.')
authorization_header = api.parser()
authorization_header.add_argument('Authorization', type=str, location='headers', help='Access token', required=True)


# User model
user_model = api.model('User', {
    'email': fields.String(required=True, description='Email'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'title': fields.String(description='Title'),
    'gender': fields.String(description='Gender'),
    'bio': fields.String(description='User Bio')
})



# signup model
signup_model = api.model('Signup', {
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')
})

# profile model
profile_model = api.model('Profile', {
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'email': fields.String(description='Email'),
    'title': fields.String(description='Title'),
    'bio': fields.String(description='User Bio')
})

edit_profile_model = api.model('EditProfile', {
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'title': fields.String(description='Title'),
    'bio': fields.String(description='User Bio')
})

expense_model = api.model('Expense', {
    'description': fields.String(required=True, description='Expense description'),
    'amount': fields.Float(required=True, description='Expense amount'),
    'date': fields.Date(required=True, description='Expense date'),
})

income_model = api.model('Income', {
    'description': fields.String(required=True, description='Income description'),
    'amount': fields.Float(required=True, description='Income amount'),
    'date': fields.Date(required=True, description='Income date'),
})

invoice_model = api.model('Invoice', {
    'invoice_number': fields.String(required=True, description='Invoice number'),
    'description': fields.String(required=True, description='Invoice description'),
    'amount': fields.Float(required=True, description='Invoice amount'),
    'due_date': fields.Date(required=True, description='Invoice due date'),
    'paid': fields.Boolean(required=True, description='Invoice payment status'),
    'invoice_type': fields.String(required=True, description='Invoice type (income or expense)'),
    'customer_id': fields.Integer(description='customer ID'),
    'supplier_id': fields.Integer(description='Supplier ID')
})

transaction_model = api.model('Transaction', {
    'invoice_number': fields.String(required=True, description='Invoice number'),
    'invoice_type': fields.String(required=True, description='Invoice type (income or expense)')
})


supplier_model = api.model('Supplier', {
    'name': fields.String(required=True, description='Supplier name'),
    'email': fields.String(required=True, description='Supplier email')
})

customer_model = api.model('Customer', {
    'name': fields.String(required=True, description='Customer name'),
    'email': fields.String(required=True, description='Customer email')
})

# Define the revenue model for serialization
revenue_model = api.model('RevenueModel', {
    'start_date': fields.String(description='Start date for revenue calculation (YYYY-MM-DD)'),
    'end_date': fields.String(description='End date for revenue calculation (YYYY-MM-DD)'),
    'total_income': fields.Float(description='Total income during the specified period'),
    'total_expenses': fields.Float(description='Total expenses during the specified period'),
    'net_revenue': fields.Float(description='Net revenue (income - expenses)')
})

# User SQLAlchemy model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    title = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    bio = db.Column(db.String(200))

    expenses = db.relationship('Expense', backref='user', lazy=True)
    incomes = db.relationship('Income', backref='user', lazy=True)
    invoices = db.relationship('Invoice', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    suppliers = db.relationship('Supplier', backref='user', lazy=True)
    customers = db.relationship('Customer', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


# Expense SQLAlchemy model

# Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Foreign key to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # After creating an expense, create a corresponding transaction of type "payment made"
    def __init__(self, *args, **kwargs):
        super(Expense, self).__init__(*args, **kwargs)
        self.create_expense_transaction()

    def create_expense_transaction(self):
        new_transaction = Transaction(
            type='payment made',
            amount=self.amount,
            date=self.date,
            description=self.description,  # Include description from expense
            user=self.user
        )
        db.session.add(new_transaction)
        db.session.commit()


# Income SQLAlchemy model
# Income Model
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Foreign key to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # After creating an income, create a corresponding transaction of type "payment received"
    def __init__(self, *args, **kwargs):
        super(Income, self).__init__(*args, **kwargs)
        self.create_income_transaction()

    def create_income_transaction(self):
        new_transaction = Transaction(
            type='payment received',
            amount=self.amount,
            date=self.date,
            description=self.description,  # Include description from income
            user=self.user
        )
        db.session.add(new_transaction)
        db.session.commit()


# Invoice SQLAlchemy model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid = db.Column(db.Boolean, nullable=False)
    invoice_type = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Invoice {self.description}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    invoice_number = db.Column(db.String(20))
    description = db.Column(db.String(200))
    customer_name = db.Column(db.String(200))
    supplier_name = db.Column(db.String(200))
    status = db.Column(db.String(100), nullable=False, default='Transaction completed')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String())

    # Relationship with Invoice model

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), nullable=True)
    invoice = db.relationship('Invoice', backref='transactions')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=True)
    customer = db.relationship('Customer', backref='transactions')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id}>'


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    invoices = db.relationship('Invoice', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Supplier {self.name}>'


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    invoices = db.relationship('Invoice', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name}>'


# Create the database tables (run this once)
with app.app_context():
    db.create_all()


# API routes
@api.route('/signup')
class Signup(Resource):
    @api.expect(signup_model)
    def post(self):
        """Create a new user"""
        data = api.payload
        email = data['email']

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 409

        # Hash the password
        hashed_password = generate_password_hash(data['password'], method='sha256')

        # Create the user
        new_user = User(
            email=email,
            password=hashed_password,
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201


@api.route('/login')
class Login(Resource):
    @api.expect(api.model('Login', {
        'email': fields.String(required=True, description='Email'),
        'password': fields.String(required=True, description='Password')
    }))
    def post(self):
        """Login to the application"""
        data = api.payload
        email = data['email']
        password = data['password']

        # Find the user
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Check the password
        if not check_password_hash(user.password, password):
            return {'message': 'Invalid credentials'}, 401

        # Generate access token
        access_token = create_access_token(identity=user.email)

        return {'access_token': access_token}, 200


@api.route('/profile')
class Profile(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user profile"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user profile data
        profile_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.title,
            'bio': user.bio
        }

        return profile_data, 200


@api.route('/profile/edit')
class EditProfile(Resource):
    @jwt_required()
    @api.expect(authorization_header, edit_profile_model, validate=True)
    def post(self):
        """Edit user profile"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Update the profile details
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.title = data.get('title', user.title)
        user.bio = data.get('bio', user.bio)
        db.session.commit()

        return {'message': 'Profile updated successfully'}, 200


@api.route('/expenses')
class Expenses(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's expense transactions"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Get all expense transactions for the user from the Transaction model
        expense_transactions = Transaction.query.filter_by(type='expense', user=user).all()

        # Serialize expense transactions
        expenses_data = []
        for expense in expense_transactions:
            expense_data = {
                'id': expense.id,
                'amount': expense.amount,
                'date': expense.date.strftime('%Y-%m-%d'),
                'description': expense.description,
                'status': expense.status
            }
            expenses_data.append(expense_data)

        return expenses_data, 200



@api.route('/expenses/create')
class CreateExpense(Resource):
    @jwt_required()
    @api.expect(authorization_header, expense_model, validate=True)
    @api.response(201, 'Expense created successfully')
    def post(self):
        """Create a new expense"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the transaction for expenses
        new_transaction = Transaction(
            type='expense',
            amount=data['amount'],
            date=datetime.now(),
            description=data['description'],
            customer_name=None,
            supplier_name=None,
            status='Transaction completed',
            user=user
        )

        db.session.add(new_transaction)
        db.session.commit()

        transaction_data = {
            'id': new_transaction.id,
            'type': new_transaction.type,
            'amount': new_transaction.amount,
            'date': new_transaction.date.strftime('%Y-%m-%d'),
            'description': new_transaction.description,
            'status': new_transaction.status
        }

        return transaction_data, 201



@api.route('/incomes')
class Incomes(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's income transactions"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Get all income transactions for the user from the Transaction model
        income_transactions = Transaction.query.filter_by(type='income', user=user).all()

        # Serialize income transactions
        incomes_data = []
        for income in income_transactions:
            income_data = {
                'id': income.id,
                'amount': income.amount,
                'date': income.date.strftime('%Y-%m-%d'),
                'description': income.description,
                'status': income.status
            }
            incomes_data.append(income_data)

        return incomes_data, 200


@api.route('/incomes/create')
class CreateIncome(Resource):
    @jwt_required()
    @api.expect(authorization_header, income_model, validate=True)
    @api.response(201, 'Income created successfully')
    def post(self):
        """Create a new income"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the transaction for income
        new_transaction = Transaction(
            type='income',
            amount=data['amount'],
            date=datetime.now(),
            description=data['description'],
            customer_name=None,
            supplier_name=None,
            status='Transaction completed',
            user=user
        )

        db.session.add(new_transaction)
        db.session.commit()

        transaction_data = {
            'id': new_transaction.id,
            'type': new_transaction.type,
            'amount': new_transaction.amount,
            'date': new_transaction.date.strftime('%Y-%m-%d'),
            'description': new_transaction.description,
            'status': new_transaction.status
        }

        return transaction_data, 201


@api.route('/incomes/<int:income_id>')
class IncomeDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, income_id):
        """Get details of a specific income by ID"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the income transaction
        income_transaction = Transaction.query.filter_by(id=income_id, type='income', user=user).first()
        if not income_transaction:
            return {'message': 'Income not found'}, 404

        # Serialize income details
        income_data = {
            'id': income_transaction.id,
            'type': income_transaction.type,
            'amount': income_transaction.amount,
            'date': income_transaction.date.strftime('%Y-%m-%d'),
            'description': income_transaction.description
        }

        return income_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, income_id):
        """Delete a specific income by ID"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the income transaction
        income_transaction = Transaction.query.filter_by(id=income_id, type='income', user=user).first()
        if not income_transaction:
            return {'message': 'Income not found'}, 404

        db.session.delete(income_transaction)
        db.session.commit()

        return {'message': 'Income deleted successfully'}, 200

@api.route('/invoices')
class Invoices(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's invoices"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user's invoices
        invoices = []
        for invoice in user.invoices:
            invoice_data = {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'description': invoice.description,
                'amount': invoice.amount,
                'due_date': invoice.due_date.strftime('%Y-%m-%d'),  # Format due_date as YYYY-MM-DD
                'paid': invoice.paid,
                'invoice_type': invoice.invoice_type,
                'customer_id': invoice.customer_id,
                'supplier_id': invoice.supplier_id
            }
            invoices.append(invoice_data)

        return invoices, 200


@api.route('/transactions/create')
class CreateTransaction(Resource):
    @jwt_required()
    @api.expect(authorization_header, transaction_model, validate=True)
    @api.response(201, 'Transaction created successfully')
    def post(self):
        """Create a new transaction"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Extract provided invoice data
        invoice_number = data.get('invoice_number')
        invoice_type = data.get('invoice_type')

        if invoice_type not in ['income', 'expense']:
            return {'message': 'Invalid invoice type'}, 400

        # Find the invoice based on provided invoice number and type
        if invoice_type == 'income':
            invoice = Invoice.query.filter_by(invoice_number=invoice_number, invoice_type='income', user=user).first()
        else:
            invoice = Invoice.query.filter_by(invoice_number=invoice_number, invoice_type='expense', user=user).first()

        if not invoice:
            return {'message': 'Invoice not found'}, 404

        # Create the transaction
        new_transaction = Transaction(
            type=invoice_type,
            amount=invoice.amount,
            date=datetime.now(),
            description=invoice.description,
            customer_name=None,
            supplier_name=None,
            status='Transaction completed',
            user=user,
            invoice=invoice
        )

        db.session.add(new_transaction)
        db.session.commit()

        transaction_data = {
            'id': new_transaction.id,
            'type': new_transaction.type,
            'amount': new_transaction.amount,
            'date': new_transaction.date.strftime('%Y-%m-%d'),
            'description': new_transaction.description,
            'status': new_transaction.status
        }

        return transaction_data, 201



@api.route('/transactions')
class Transactions(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's transactions"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404
        
        

        # Serialize user's transactions
        transactions = []
        for transaction in user.transactions:
            invoice_type = transaction.invoice.invoice_type if transaction.invoice else None
            customer_name = transaction.customer.name if transaction.customer else None
            transaction_data = {
                'id': transaction.id,
                'date': transaction.date.strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
                'customer_name': transaction.customer_name,
                'supplier_name': transaction.supplier_name,
                'invoice_type': invoice_type,
                'type': transaction.type,
                'amount': transaction.amount,
                'status': 'completed' if transaction.status == 'Transaction completed' else 'incomplete',
                'invoice_number': transaction.invoice_number
            }
            transactions.append(transaction_data)

        return transactions, 200



@api.route('/invoices/create')
class CreateInvoice(Resource):
    @jwt_required()
    @api.expect(authorization_header, invoice_model, validate=True)
    @api.response(201, 'Invoice created successfully')
    def post(self):
        """Create a new invoice"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        invoice_type = data['invoice_type']
        if invoice_type == 'income':
            # Find the customer
            customer_id = data.get('customer_id')
            customer = Customer.query.filter_by(id=customer_id, user=user).first()
            if not customer:
                return {'message': 'Customer not found'}, 404
            customer_id = customer.id
            supplier_id = None
        elif invoice_type == 'expense':
            # Find the supplier
            supplier_id = data.get('supplier_id')
            supplier = Supplier.query.filter_by(id=supplier_id, user=user).first()
            if not supplier:
                return {'message': 'Supplier not found'}, 404
            supplier_id = supplier.id
            customer_id = None
        else:
            return {'message': 'Invalid invoice type'}, 400

        # Create the invoice
        new_invoice = Invoice(
            invoice_number=data['invoice_number'],
            description=data['description'],
            amount=data['amount'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d'),
            paid=data['paid'],
            invoice_type=invoice_type,
            customer_id=customer_id,
            supplier_id=supplier_id,
            user=user
        )

        db.session.add(new_invoice)
        db.session.commit()

        return {'message': 'Invoice created successfully'}, 201


@api.route('/suppliers')
class Suppliers(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's suppliers with associated invoices"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user's suppliers with associated invoices
        suppliers = []
        for supplier in user.suppliers:
            supplier_data = {
                'id': supplier.id,
                'name': supplier.name,
                'email': supplier.email,
                'invoices': []
            }
            for invoice in supplier.invoices:
                invoice_data = {
                    'invoice_number': invoice.invoice_number,
                    'invoice_type': invoice.invoice_type,
                    'description': invoice.description,
                    'paid': invoice.paid,
                    'due_date': invoice.due_date.strftime('%Y-%m-%d')
                }
                supplier_data['invoices'].append(invoice_data)
            suppliers.append(supplier_data)

        return suppliers, 200


@api.route('/suppliers/create')
class CreateSupplier(Resource):
    @jwt_required()
    @api.expect(authorization_header, supplier_model, validate=True)
    @api.response(201, 'Supplier created successfully')
    def post(self):
        """Create a new supplier"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the supplier
        new_supplier = Supplier(
            name=data['name'],
            email=data['email'],
            user=user
        )

        db.session.add(new_supplier)
        db.session.commit()

        return {'message': 'Supplier created successfully'}, 201


@api.route('/customers')
class Customers(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's customers with associated invoices"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user's customers with associated invoices
        customers = []
        for customer in user.customers:
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'invoices': []
            }
            for invoice in customer.invoices:
                invoice_data = {
                    'invoice_number': invoice.invoice_number,
                    'invoice_type': invoice.invoice_type,
                    'description': invoice.description,
                    'paid': invoice.paid,
                    'due_date': invoice.due_date.strftime('%Y-%m-%d')
                }
                customer_data['invoices'].append(invoice_data)
            customers.append(customer_data)

        return customers, 200


@api.route('/customers/create')
class CreateCustomer(Resource):
    @jwt_required()
    @api.expect(authorization_header, customer_model, validate=True)
    @api.response(201, 'Customer created successfully')
    def post(self):
        """Create a new customer"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the customer
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            user=user
        )

        db.session.add(new_customer)
        db.session.commit()

        return {'message': 'Customer created successfully'}, 201


@api.route('/suppliers')
class Suppliers(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's suppliers with associated invoices"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user's suppliers with associated invoices
        suppliers = []
        for supplier in user.suppliers:
            supplier_data = {
                'id': supplier.id,
                'name': supplier.name,
                'email': supplier.email,
                'invoices': []
            }
            for invoice in supplier.invoices:
                invoice_data = {
                    'invoice_number': invoice.invoice_number,
                    'invoice_type': invoice.invoice_type,
                    'description': invoice.description,
                    'paid': invoice.paid,
                    'due_date': invoice.due_date.strftime('%Y-%m-%d')
                }
                supplier_data['invoices'].append(invoice_data)
            suppliers.append(supplier_data)

        return suppliers, 200


@api.route('/suppliers/create')
class CreateSupplier(Resource):
    @jwt_required()
    @api.expect(authorization_header, supplier_model, validate=True)
    @api.response(201, 'Supplier created successfully')
    def post(self):
        """Create a new supplier"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the supplier
        new_supplier = Supplier(
            name=data['name'],
            email=data['email'],
            user=user
        )

        db.session.add(new_supplier)
        db.session.commit()

        return {'message': 'Supplier created successfully'}, 201


@api.route('/customers')
class Customers(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self):
        """Get user's customers with associated invoices"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Serialize user's customers with associated invoices
        customers = []
        for customer in user.customers:
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'invoices': []
            }
            for invoice in customer.invoices:
                invoice_data = {
                    'invoice_number': invoice.invoice_number,
                    'invoice_type': invoice.invoice_type,
                    'description': invoice.description,
                    'paid': invoice.paid,
                    'due_date': invoice.due_date.strftime('%Y-%m-%d')
                }
                customer_data['invoices'].append(invoice_data)
            customers.append(customer_data)

        return customers, 200


@api.route('/customers/create')
class CreateCustomer(Resource):
    @jwt_required()
    @api.expect(authorization_header, customer_model, validate=True)
    @api.response(201, 'Customer created successfully')
    def post(self):
        """Create a new customer"""
        current_user_email = get_jwt_identity()
        data = api.payload

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Create the customer
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            user=user
        )

        db.session.add(new_customer)
        db.session.commit()

        return {'message': 'Customer created successfully'}, 201

# Additional routes for expanded views and delete operations

@api.route('/customers/<int:customer_id>')
class CustomerDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, customer_id):
        """Get details of a specific customer"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the customer
        customer = Customer.query.filter_by(id=customer_id, user=user).first()
        if not customer:
            return {'message': 'Customer not found'}, 404

        # Serialize customer details
        customer_data = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'invoices': []
        }
        for invoice in customer.invoices:
            invoice_data = {
                'invoice_number': invoice.invoice_number,
                'invoice_type': invoice.invoice_type,
                'description': invoice.description,
                'paid': invoice.paid,
                'due_date': invoice.due_date.strftime('%Y-%m-%d')
            }
            customer_data['invoices'].append(invoice_data)

        return customer_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, customer_id):
        """Delete a specific customer"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the customer
        customer = Customer.query.filter_by(id=customer_id, user=user).first()
        if not customer:
            return {'message': 'Customer not found'}, 404

        db.session.delete(customer)
        db.session.commit()

        return {'message': 'Customer deleted successfully'}, 204  # 204 No Content

@api.route('/suppliers/<int:supplier_id>')
class SupplierDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, supplier_id):
        """Get details of a specific supplier"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404


        # Find the supplier
        supplier = Supplier.query.filter_by(id=supplier_id, user=user).first()
        if not supplier:
            return {'message': 'Supplier not found'}, 404

        # Serialize supplier details
        supplier_data = {
            'id': supplier.id,
            'name': supplier.name,
            'email': supplier.email,
            'invoices': []
        }
        for invoice in supplier.invoices:
            invoice_data = {
                'invoice_number': invoice.invoice_number,
                'description': invoice.description,
                'amount': invoice.amount,
                'due_date': invoice.due_date.strftime('%Y-%m-%d'),
                'paid': invoice.paid,
                'invoice_type': invoice.invoice_type,
                'customer_id': invoice.customer_id,
                'supplier_id': invoice.supplier_id
            }
            supplier_data['invoices'].append(invoice_data)

        return supplier_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, supplier_id):
        """Delete a specific supplier"""
        current_user_email = get_jwt_identity()

        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404


        # Find the supplier
        supplier = Supplier.query.filter_by(id=supplier_id, user=user).first()
        if not supplier:
            return {'message': 'Supplier not found'}, 404

        db.session.delete(supplier)
        db.session.commit()

        return {'message': 'Supplier deleted successfully'}, 200


@api.route('/transactions/<int:transaction_id>')
class TransactionDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, transaction_id):
        """Get details of a specific transaction"""
        current_user_email = get_jwt_identity()

        # Find the transaction
        transaction = Transaction.query.filter_by(id=transaction_id).join(Transaction.user).filter_by(email=current_user_email).first()
        if not transaction:
            return {'message': 'Transaction not found'}, 404

        # Serialize transaction details
        transaction_data = {
            'id': transaction.id,
            'type': transaction.type,
            'amount': transaction.amount,
            'date': transaction.date.strftime('%Y-%m-%d')
        }

        return transaction_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, transaction_id):
        """Delete a specific transaction"""
        current_user_email = get_jwt_identity()

        # Find the transaction
        transaction = Transaction.query.filter_by(id=transaction_id).join(Transaction.user).filter_by(email=current_user_email).first()
        if not transaction:
            return {'message': 'Transaction not found'}, 404

        db.session.delete(transaction)
        db.session.commit()

        return {'message': 'Transaction deleted successfully'}, 200


@api.route('/expenses/<int:expense_id>')
class ExpenseDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, expense_id):
        """Get details of a specific expense by ID"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the expense transaction
        expense_transaction = Transaction.query.filter_by(id=expense_id, type='expense', user=user).first()
        if not expense_transaction:
            return {'message': 'Expense not found'}, 404

        # Serialize expense details
        expense_data = {
            'id': expense_transaction.id,
            'type': expense_transaction.type,
            'amount': expense_transaction.amount,
            'date': expense_transaction.date.strftime('%Y-%m-%d'),
            'description': expense_transaction.description
        }

        return expense_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, expense_id):
        """Delete a specific expense by ID"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the expense transaction
        expense_transaction = Transaction.query.filter_by(id=expense_id, type='expense', user=user).first()
        if not expense_transaction:
            return {'message': 'Expense not found'}, 404

        db.session.delete(expense_transaction)
        db.session.commit()

        return {'message': 'Expense deleted successfully'}, 200

@api.route('/invoices/<int:invoice_id>')
class InvoiceDetails(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    def get(self, invoice_id):
        """Get details of a specific invoice"""
        current_user_email = get_jwt_identity()

        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the invoice
        invoice = Invoice.query.filter_by(id=invoice_id, user=user).first()
        if not invoice:
            return {'message': 'Invoice not found'}, 404

        # Serialize invoice details
        invoice_data = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'description': invoice.description,
            'amount': invoice.amount,
            'due_date': invoice.due_date.strftime('%Y-%m-%d'),
            'paid': invoice.paid,
            'invoice_type': invoice.invoice_type,
            'customer_id': invoice.customer_id,
            'supplier_id': invoice.supplier_id
        }

        return invoice_data, 200

    @jwt_required()
    @api.doc(parser=authorization_header)
    def delete(self, invoice_id):
        """Delete a specific invoice"""
        current_user_email = get_jwt_identity()

        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Find the invoice
        # Find the invoice
        invoice = Invoice.query.filter_by(id=invoice_id, user=user).first()
        if not invoice:
            return {'message': 'Invoice not found'}, 404

        # Check if the current user is authorized to delete the invoice
        if invoice.user.email != current_user_email:
            return {'message': 'Unauthorized to delete this invoice'}, 403

        # Delete the invoice from the database
        db.session.delete(invoice)
        db.session.commit()

        return {'message': 'Invoice deleted successfully'}, 200



@api.route('/revenue')
class Revenue(Resource):
    @jwt_required()
    @api.doc(parser=authorization_header)
    @api.param('start_date', description='Start date for revenue calculation (YYYY-MM-DD)', type='string', required=True)
    @api.param('end_date', description='End date for revenue calculation (YYYY-MM-DD)', type='string', required=True)
    @api.marshal_with(revenue_model, code=200)
    def get(self):
        """Calculate revenue for a specific period"""
        current_user_email = get_jwt_identity()

        # Find the user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Get the start date and end date from query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return {'message': 'Start date and end date are required query parameters'}, 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return {'message': 'Invalid date format. Please use YYYY-MM-DD format.'}, 400

        # Calculate total income and total expenses from transactions within the specified period
        total_income = 0
        total_expenses = 0

        for transaction in user.transactions:
            if start_date <= transaction.date <= end_date:
                if transaction.type == 'income':
                    total_income += transaction.amount
                elif transaction.type == 'expense':
                    total_expenses += transaction.amount

        # Calculate net revenue (income - expenses)
        net_revenue = total_income - total_expenses

        return {
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_revenue': net_revenue
        }, 200








if __name__ == '__main__':
    app.run(debug=True)




#cust,inv,transact,supp