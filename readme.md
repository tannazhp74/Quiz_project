## Flask RESTful API with SQLAlchemy and Redis Integration

This is a sample README for a Flask application that demonstrates how to create a RESTful API using Flask, integrate SQLAlchemy for database operations, and use Redis for caching.

**Table of Contents**
* Project Description
* Features
* Prerequisites
* Installation
* Getting Started
* API Endpoints
* Creating Database Migrations
* Running the Application
* Testing the API
* Swagger Documentation
* Project Description


This Flask application serves as a template for creating a RESTful API with features such as token-based authentication, database operations using SQLAlchemy, and data caching with Redis.

### Features

Flask RESTful API: Build a RESTful API using Flask to handle various HTTP requests.

SQLAlchemy Integration: Use SQLAlchemy for working with the database, creating models, and performing database operations.

Token-Based Authentication: Implement token-based authentication to secure API endpoints.

Redis Caching: Store and retrieve data in Redis for improved performance and reduced database load.

Database Migrations: Manage database schema changes and versioning using Alembic.

Swagger Documentation: Automatically generate API documentation using Flask-RESTx.

Unit Testing: Implement unit tests for your API endpoints.

### Prerequisites

Before you start, ensure you have the following prerequisites installed:

* Python 3.10
* Flask
* Flask-RESTx
* SQLAlchemy
* Redis
* Alembic (for database migrations)
* Any other project-specific dependencies

### Installation

* Python version >= 3.10


* Clone the repository:

    ```
    git clone https://github.com/your-username/your-flask-app.git
    cd your-flask-app
    ```

* Create a virtual environment (recommended) and activate it:

    ```
    python -m venv venv
    venv/bin/activate
    ```

* Install the project dependencies:

    `pip install -r requirements.txt`


* Database Setup

    Create your database and update the database URL in your configuration file.
    in this project we used postgreSQL.
    `SQLALCHEMY_DATABASE_URI=postgresql://<username>:<password>@localhost/<database name>`


* Redis Setup

    Configure Redis settings, including the Redis server host and port, in your configuration file.
    Adding Token Authentication

* Create tables  
    `flask db init `
    after initializing db, add your models address to env.py file inside migrations directory 
    then run 
    `flask db migrate`
    and then 
    `flask db upgrade` for building tables inside your database.
    
  

### API Endpoints
* **Home or Health checker**
    By calling this api you can check the health of server and connection
  
    `/`


* **User Management**
    <br>
    <br>
  
    Create User: Create a new user account.   
    `POST /api/users`
    <br>
    <br>
    **Login:** Authenticate a user and generate an access token.

    `POST /api/login`


* **Card Management**
    <br>
    <br>
    Create Card: Create a new card for a user.

    `POST /api/cards`
    <br>
    <br>
    Update Card: Update card details.

    `PUT /api/cards`
    <br>
    <br>
    List Cards: Get a list of all user cards.

    `GET /api/list_cards`
    <br>
    <br>
    Delete card: Delete a specific card
  
    `DELETE /delete_card/<int:card_id>`

    
* **Transactions** 
    <br>
    <br>
    Create transaction: Create and add a new transaction for user.
  
    `POST /create_transaction`
    <br>
    <br>
  
    List transactions: List transactions in both 'detailed by description' and 'summary' options
    
    `POST /list_transactions`

### Running the Application

Start the Flask development server:

`flask run`

Your Flask application will be accessible at http://localhost:5001.

### Testing the API

Run unit tests to ensure your API endpoints work correctly:

`pytest`

### Swagger Documentation

Access the Swagger documentation for your API by visiting `/v1/doc ` in your web browser.

### How to add additional API endpoints?

To add more API endpoints, create new resources and namespaces using Flask-RESTx. Define the route, request/response models, and business logic for each endpoint.

### How do I customize the Swagger documentation?

You can customize the Swagger documentation by adding documentation strings and security definitions to your endpoints and models. Use the @quiz_namespace.doc and @quiz_namespace.expect decorators for this purpose.

### How do I handle database schema changes?

Use Alembic to manage database schema changes. Create and apply migrations to update your database schema as needed.
