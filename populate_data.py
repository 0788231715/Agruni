import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')
django.setup()

from accounts.models import User
from services.models import Service, WasteCategory
from collection.models import Vehicle

def populate():
    print("Populating sample data...")

    # Create Superuser if doesn't exist
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@wmrs.rw", "admin123", role=User.Role.ADMIN)
        print("Admin created.")

    # Create Categories
    categories = [
        ("Plastic", "Bottles, containers, etc.", True),
        ("Paper", "Cardboard, office paper", True),
        ("Organic", "Food waste, garden waste", True),
        ("Glass", "Bottles, jars", True),
        ("Hazardous", "Batteries, chemicals", False),
    ]
    for name, desc, recyc in categories:
        WasteCategory.objects.get_or_create(name=name, description=desc, is_recyclable=recyc)

    # Create Services
    services = [
        ("Residential Collection", "Weekly pickup for households.", "COLLECTION", 5000),
        ("Commercial Collection", "Daily pickup for businesses.", "COLLECTION", 25000),
        ("Industrial Recycling", "Large scale sorting and processing.", "RECYCLING", 100000),
    ]
    for title, desc, stype, price in services:
        Service.objects.get_or_create(title=title, description=desc, service_type=stype, price=Decimal(price))

    # Create Vehicles
    vehicles = [
        ("RAE 123 A", "ISUZU Compactor", 5000),
        ("RAB 456 B", "Mitsubishi Canter", 3000),
        ("RAC 789 C", "HINO Tipper", 7000),
    ]
    for plate, model, cap in vehicles:
        Vehicle.objects.get_or_create(plate_number=plate, model=model, capacity_kg=Decimal(cap))

    # Create Staff
    staff_roles = [
        ("driver1", User.Role.DRIVER),
        ("driver2", User.Role.DRIVER),
        ("finance1", User.Role.FINANCE),
        ("supervisor1", User.Role.SUPERVISOR),
        ("recycling1", User.Role.SORTING_STAFF),
    ]
    for uname, role in staff_roles:
        if not User.objects.filter(username=uname).exists():
            User.objects.create_user(uname, f"{uname}@wmrs.rw", "password123", role=role)

    print("Population complete.")

if __name__ == "__main__":
    populate()
