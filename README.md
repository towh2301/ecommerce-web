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

## 7) App overview and key URLs
Root URL configuration: ProjectB_Final/urls.py
- '' -> includes home.urls
- 'admin/' -> Django admin
- 'oauth/' -> social auth routes
- 'api/address/' -> vi_address routes
- 'vnpay/' -> VNPay API routes

Home app routes (home/urls.py) include:
- '' -> Homepage
- 'menu/', 'about/', 'book-table/'
- Auth: 'login/', 'logout/'
- Product details: 'product/<slug>/'
- Cart: 'add-to-cart/', 'cart-summary/' (+ helper endpoints)
- Checkout and payments: 'checkout/', 'payment/', 'payment_return/'
- User profile and password reset flows
- REST API endpoints under 'api/...'

Note: The REST Framework default permission is IsAuthenticated, so you must log in to call most API endpoints.

## 8) Optional integrations you may want to configure
These are already wired in settings.py with placeholders/sandbox values. For production, move secrets to environment variables and update values accordingly.

- Social Auth (Facebook/Twitter/GitHub):
  - SOCIAL_AUTH_FACEBOOK_KEY, SOCIAL_AUTH_FACEBOOK_SECRET are set to sample values.
  - You must create your own apps/keys for production or disable these backends.

- Email (for password reset):
  - EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are empty. Supply your Gmail credentials or app password, or switch to console backend for local testing:
    ```python
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    ```

- VNPay sandbox:
  - VNPAY_* values are preset for sandbox. Keep them for testing. Ensure VNPAY_RETURN_URL matches your local host/port if you change it.

- Google Maps API:
  - GOOGLE_MAPS_API_KEY is present. Replace with your own key if needed.

## 9) Static and media files
- STATICFILES_DIRS already includes /static and /home/static
- MEDIA files served under /media
Django serves these in development via settings in ProjectB_Final/urls.py.

## 10) Seed sample data (optional)
To explore the UI quickly, you can create Items via the Django admin or the API after logging in.

## 11) Common troubleshooting
- mysqlclient install fails on Windows:
  - Ensure MySQL Server and MySQL Connector/C (or Visual C++ Build Tools) are installed.
  - Try precompiled wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
  - As a temporary workaround for development, switch to SQLite (see section 4).

- Access to API returns 403 or asks for login:
  - REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES = IsAuthenticated. Log in via web and then call API endpoints.

- Payment return URL not hit:
  - Confirm VNPAY_RETURN_URL matches your dev server URL.

- Email not sending:
  - For local dev, use the console backend during iteration.

## 12) One-command local run (Windows)
Prefer using the helper script that automates the full flow (venv, install, migrate, run):

PowerShell:
```powershell
# From the repository root
./run-all.ps1
```

Command Prompt (CMD):
```bat
run-all.bat
```

Options:
- Create superuser non-interactively:
  ```powershell
  ./run-all.ps1 -CreateSuperuser -Username admin -Password P@ssw0rd! -Email admin@example.com
  ```
- Use a different port (default 8000):
  ```powershell
  ./run-all.ps1 -Port 8080
  ```
- Skip starting the server (e.g., in CI):
  ```powershell
  ./run-all.ps1 -NoServer
  ```

## 13) Next steps
- Add .env support (e.g., using python-dotenv or django-environ) to simplify setup.
- Replace hardcoded secrets in settings.py with environment variables.
- Write seeds/fixtures for sample products and categories.

If you need help starting the server on your machine, tell me your Python and MySQL versions and I’ll tailor the exact commands for you.