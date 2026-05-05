# Waste Management and Recycling System (WMRS)

## Project Overview
WMRS is a comprehensive digital platform designed for waste management companies like Agruni Rwanda. It automates customer service, logistics, recycling, and financial operations.

## Features
- **Public Website:** Professional landing page, services, and contact info.
- **Role-Based Dashboards:** 8 distinct user roles (Admin, Manager, Customer, Driver, Supervisor, Finance, Recycling).
- **Logistics Management:** Vehicle and route tracking, driver assignments.
- **Recycling Module:** Waste classification and recycling performance tracking.
- **Financial Module:** Automated invoicing and payment status monitoring.
- **Customer Service:** Pickup requests and complaint management.

## Tech Stack
- **Backend:** Django 5.2.8
- **Frontend:** Bootstrap 5, Chart.js, HTML5/CSS3
- **Database:** SQLite (Production-ready with PostgreSQL support)

## Installation & Running

1. **Install Dependencies:**
   ```bash
   pip install django django-crispy-forms crispy-bootstrap5 pillow django-countries
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Populate Sample Data:**
   ```bash
   python populate_data.py
   ```

4. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the System:**
   - **Frontend:** http://127.0.0.1:8000
   - **Admin Dashboard:** http://127.0.0.1:8000/admin (User: `admin`, Pass: `admin123`)
   - **Staff/Customer Dashboards:** Login via the main website.

## Credentials for Testing
- **Admin:** `admin` / `admin123`
- **Driver:** `driver1` / `password123`
- **Supervisor:** `supervisor1` / `password123`
- **Customer:** Register a new account via the UI.
