# FinTrack-API

Discover the all-inclusive power of FinTrack API - the ultimate financial management solution. Seamlessly handle transactions, track expenses and incomes, and effortlessly manage customers and suppliers. Take control of your invoicing process and gain valuable insights into your financial health with revenue calculation capabilities. With robust authentication and powerful features, FinTrack API ensures the utmost security for your sensitive financial data, empowering you with efficient financial tracking and management. Whether you're a business owner seeking streamlined financial control or an individual aiming for better financial organization, FinTrack API is your trusted companion on the path to financial success. Embrace a brighter financial future with FinTrack API today.


![Alt text](https://github.com/cy-cus/FinTrack-API/blob/main/fintrack.png)



# Features:

## Supplier and Customer Management:
The API enables users to efficiently manage their suppliers and customers. Users can add new suppliers and customers by providing relevant details such as names and email addresses. The API allows users to view and delete these entities, facilitating seamless organization of business relationships.

## Invoice Management:
Users can create, view, and manage invoices associated with their suppliers and customers. Each invoice contains essential details, including invoice numbers, descriptions, due dates, and payment status. The API allows users to delete invoices when necessary, ensuring accurate financial records.

## Expense Tracking:
With the ability to add, view, and delete expenses, the API provides a robust expense tracking mechanism. Users can record each expense's amount, description, and date, enabling better control over expenditure.

## Income Tracking (Invoices as Income):
The Financial Management API considers invoices with the "income" type, representing payments received from customers. This ensures a complete financial overview, including income and expenses, for a comprehensive financial management experience.

## Revenue Calculation:
The API offers revenue calculation capabilities, allowing users to analyze their financial performance for specific periods. By providing start and end dates, users can calculate total income, total expenses, and net revenue, gaining valuable insights into their financial health.

## Authentication and Authorization:
To protect sensitive financial data, the API employs JWT tokens for authentication and authorization. Only authorized users with valid tokens and permisions can access protected endpoints, ensuring data security and privacy.

# API Endpoints
```
/suppliers
/suppliers/create
/suppliers/<int:supplier_id>
/customers
/customers/create
/customers/<int:customer_id>
/transactions
/transactions/create
/transactions/<int:transaction_id>
/expenses
/expenses/create
/expenses/<int:expense_id>
/incomes
/incomes/create
/incomes/<int:income_id>
/invoices
/invoices/create
/invoices/<int:invoice_id
/revenue
/profile
/profile/edit
/signup
/login
```




### /suppliers

Method: GET

Description: This endpoint allows users to retrieve a list of suppliers along with their associated invoices. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of suppliers, where each supplier object includes information like id, name, email, and a list of invoices. Each invoice contains details such as invoice_number, invoice_type, description, paid, and due_date.

### /suppliers/create

Method: POST

Description: This endpoint enables users to create a new supplier. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new supplier in the request body following the supplier_model schema.
Response: If successful, the API will return a message indicating that the supplier has been created successfully.

### /suppliers/<int:supplier_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific supplier (identified by supplier_id) or delete the supplier if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified supplier, including associated invoices.
Response (DELETE): If successful, the API will return a message indicating that the supplier has been deleted successfully.

### /customers

Method: GET

Description: This endpoint allows users to retrieve a list of customers along with their associated invoices. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of customers, where each customer object includes information like id, name, email, and a list of invoices. Each invoice contains details such as invoice_number, invoice_type, description, paid, and due_date.

### /customers/create

Method: POST

Description: This endpoint enables users to create a new customer. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new customer in the request body following the customer_model schema.
Response: If successful, the API will return a message indicating that the customer has been created successfully.

### /customers/<int:customer_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific customer (identified by customer_id) or delete the customer if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified customer, including associated invoices.
Response (DELETE): If successful, the API will return a message indicating that the customer has been deleted successfully.

### /transactions

Method: GET

Description: This endpoint allows users to retrieve a list of all transactions associated with their account. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of transactions, each containing information like id, type (income or expense), amount, and date.

### /transactions/create

Method: POST

Description: This endpoint enables users to create a new transaction, whether it's an income or expense. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new transaction in the request body following the transaction_model schema.
Response: If successful, the API will return a message indicating that the transaction has been created successfully.

### /transactions/<int:transaction_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific transaction (identified by transaction_id) or delete the transaction if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified transaction, including information like id, type (income or expense), amount, and date.
Response (DELETE): If successful, the API will return a message indicating that the transaction has been deleted successfully.

### /expenses

Method: GET

Description: This endpoint allows users to retrieve a list of all expense transactions associated with their account. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of expense transactions, each containing information like id, amount, date, and description.

### /expenses/create

Method: POST

Description: This endpoint enables users to create a new expense transaction. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new expense transaction in the request body following the transaction_model schema.
Response: If successful, the API will return a message indicating that the expense transaction has been created successfully.

### /expenses/<int:expense_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific expense transaction (identified by expense_id) or delete the expense transaction if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified expense transaction, including information like id, amount, date, and description.
Response (DELETE): If successful, the API will return a message indicating that the expense transaction has been deleted successfully.

### /incomes

Method: GET

Description: This endpoint allows users to retrieve a list of all income transactions associated with their account. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of income transactions, each containing information like id, amount, date, and description.

### /incomes/create

Method: POST

Description: This endpoint enables users to create a new income transaction. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new income transaction in the request body following the transaction_model schema.
Response: If successful, the API will return a message indicating that the income transaction has been created successfully.

### /incomes/<int:income_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific income transaction (identified by income_id) or delete the income transaction if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified income transaction, including information like id, amount, date, and description.
Response (DELETE): If successful, the API will return a message indicating that the income transaction has been deleted successfully.

### /invoices

Method: GET

Description: This endpoint allows users to retrieve a list of all invoices associated with their account. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns a list of invoices, each containing information like id, invoice_number, description, amount, due_date, paid, invoice_type, customer_id, and supplier_id.

### /invoices/create

Method: POST

Description: This endpoint enables users to create a new invoice. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header. Users must provide the necessary information for the new invoice in the request body following the invoice_model schema.
Response: If successful, the API will return a message indicating that the invoice has been created successfully.

### /invoices/<int:invoice_id>

Method: GET, DELETE

Description: This endpoint allows users to view the details of a specific invoice (identified by invoice_id) or delete the invoice if they have the required authorization. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response (GET): Returns the details of the specified invoice, including information like id, invoice_number, description, amount, due_date, paid, invoice_type, customer_id, and supplier_id.
Response (DELETE): If successful, the API will return a message indicating that the invoice has been deleted successfully.

### /revenue

Method: GET

Description: This endpoint calculates the revenue for a specific period specified by the start_date and end_date query parameters. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Query Parameters: start_date (Start date for revenue calculation in the format YYYY-MM-DD) and end_date (End date for revenue calculation in the format YYYY-MM-DD).
Response: Returns the calculated revenue, total income, total expenses, and net revenue (income - expenses) for the specified period.

### /profile

Method: GET

Description: This endpoint allows users to view their own profile details. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Response: Returns the user's profile details, including information like id, name, and email.

### /profile/edit

Method: PUT

Description: This endpoint allows users to update their own profile details. The API requires the user to be authenticated using a JWT (JSON Web Token) through the authorization_header.
Request Body: Expects updated profile data in JSON format.
Response: If successful, returns a message indicating the successful update of the user's profile.

### /signup

Method: POST

Description: This endpoint allows users to register a new account by providing user registration data in JSON format in the request body.
Response: If successful, returns a message indicating successful user registration.

### /login

Method: POST

Description: This endpoint allows users to authenticate using their login credentials (email and password) in JSON format in the request body. Upon successful authentication, the API will generate a JWT (JSON Web Token) for further authenticated requests.
Response: If successful, returns a JWT for further authenticated requests.

### Dependencies:

Python 3.x
Flask (web framework)
Flask-RESTful (extension for building RESTful APIs)
Flask-JWT-Extended (extension for JWT authentication)
SQLAlchemy (ORM for working with databases)
SQLite (database engine, or use your preferred database)

### How to Run the Application:

Ensure you have Python and required dependencies installed (see Dependencies section).
Run the application using python main.py
The API will be available at http://localhost:5000.

