# Waste Management and Recycling System (WMRS)

## Professional WMRS Platform for Agruni-like Operations

This system is designed to handle the full operational lifecycle of a waste management company, from front-line collection to top-level financial reporting.

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install django django-crispy-forms crispy-bootstrap5 pillow django-countries
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Populate Real-World Data:**
   ```bash
   python populate_data.py
   ```

4. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## 👥 Login Credentials (Password for all: `password123`)

| Role | Username |
| :--- | :--- |
| **Admin / Boss** | `admin` (Pass: `admin123`) |
| **Secretary** | `secretary1` |
| **General Manager** | `gm1` |
| **Location Manager** | `loc_mgr1` |
| **Collector** | `collector1` |
| **Finance Officer** | `finance1` |
| **Supervisor** | `supervisor1` |
| **Driver** | `driver1` |
| **Sorting Staff** | `sorting1` |
| **Customer** | `customer1` |

## ✨ Key Features
- **10 Specialized Dashboards:** Tailored interfaces for every employee type.
- **Location Management:** Hierarchical zones (District > Sector > Zone).
- **Service Agreements:** Record custom fees and collection frequencies for every client.
- **Hierarchical Payments:** Secure flow of money from Collector to Admin.
- **Financial Analytics:** Real-time Revenue, Cost, and Profit tracking.
- **Fleet Management:** Vehicle status and driver assignments.
- **Responsive Design:** Mobile-friendly Bootstrap 5 UI for field staff.

## 🛠 Tech Stack
- Django 5.x
- Bootstrap 5 & Bi-Icons
- SQLite (Default)
- Chart.js (Dashboard Analytics)

## 📄 Documentation
See `DESIGN.md` for detailed architecture, DFDs, and Sequence Diagrams.
