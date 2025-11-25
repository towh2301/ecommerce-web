# Ecommerce Web – Developer Quick Start

This repository contains a Django 4.2 project called ProjectB_Final with a food/ecommerce app named home. Follow this guide to set up and run the project locally on Windows.

## 1) Prerequisites
- Python 3.10+ (recommended)
- Git
- Node.js (optional; only if you want to re-build frontend assets)
- MySQL Server 8.x with a user that can create/read/write a database
- A virtual environment tool (built-in venv is fine)

Packages used by the project (installed via pip):
- Django 4.2
- mysqlclient (MySQL driver)
- djangorestframework
- social-auth-app-django
- vi-address (Vietnam address)
- vnpay (VNPay integration)

Tip: On Windows, installing mysqlclient may require MySQL headers. If you have trouble, see the Troubleshooting section for alternatives.

## 2) Clone and create a virtual environment
```powershell
cd D:\Data\myself\Projects
git clone <this-repo-or-copy>
cd ecommerce-web
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) Install dependencies
Preferred:
```powershell
pip install -r requirements.txt
```

If you prefer manual installs:
```powershell
pip install "Django>=4.2,<5.0"
pip install mysqlclient djangorestframework social-auth-app-django django-vi-address django-vnpay Pillow googlemaps geopy
```

If mysqlclient fails to install on Windows, see Troubleshooting for workarounds.

## 4) Database setup
By default, the project uses SQLite for the fastest local start. No database setup is required.

Optional: Use MySQL instead
If you prefer MySQL, create a database and update ProjectB_Final/settings.py accordingly.

1) Create the database in MySQL
- Run: `CREATE DATABASE projectb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

2) Update DATABASES in ProjectB_Final/settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'projectb',
        'USER': 'root',          # change to your MySQL user
        'PASSWORD': '',          # set your password
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```
You can switch between SQLite and MySQL at any time during development.

## 5) Run migrations and create a superuser
```powershell
py manage.py migrate
py manage.py createsuperuser
```

## 6) Run the development server
```powershell
py manage.py runserver
```
The site will be available at:
- Frontend: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 13) Next steps
- Add .env support (e.g., using python-dotenv or django-environ) to simplify setup.
- Replace hardcoded secrets in settings.py with environment variables.
- Write seeds/fixtures for sample products and categories.

If you need help starting the server on your machine, tell me your Python and MySQL versions and I’ll tailor the exact commands for you.
