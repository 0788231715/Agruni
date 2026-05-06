import os
import django
import random
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')
django.setup()

from accounts.models import User
from services.models import Service, WasteCategory
from collection.models import Vehicle, District, Sector, Zone, Subscription, ServiceRequest
from payments.models import Expense, Invoice, Payment, MoneyHandover

def get_random_kigali_coords():
    # Roughly center of Kigali: -1.9441, 30.0619
    lat = Decimal("-1.94") + Decimal(str(random.uniform(-0.05, 0.05)))
    lon = Decimal("30.06") + Decimal(str(random.uniform(-0.05, 0.05)))
    return lat, lon

def populate():
    print("Populating professional real-world WMRS data with Map Coordinates...")

    # 1. Admin/Boss
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@agruni.rw", "admin123", role=User.Role.ADMIN)
    
    # 2. Locations
    kigali, _ = District.objects.get_or_create(name="Kigali")
    nyarugenge, _ = Sector.objects.get_or_create(district=kigali, name="Nyarugenge")
    kicukiro, _ = Sector.objects.get_or_create(district=kigali, name="Kicukiro")
    
    zone_a, _ = Zone.objects.get_or_create(sector=nyarugenge, name="Zone A (Town Center)")
    zone_b, _ = Zone.objects.get_or_create(sector=kicukiro, name="Zone B (Residential)")

    # 3. Roles Population
    roles_to_create = [
        ("secretary1", User.Role.SECRETARY, "Secretary Sarah"),
        ("gm1", User.Role.GENERAL_MANAGER, "GM Kagabo"),
        ("loc_mgr1", User.Role.LOCATION_MANAGER, "LocMgr John"),
        ("loc_mgr2", User.Role.LOCATION_MANAGER, "LocMgr Mary"),
        ("finance1", User.Role.FINANCE, "Finance Fred"),
        ("supervisor1", User.Role.SUPERVISOR, "Supervisor Sam"),
        ("collector1", User.Role.COLLECTOR, "Collector Paul"),
        ("collector2", User.Role.COLLECTOR, "Collector Jean"),
        ("collector3", User.Role.COLLECTOR, "Collector Eric"),
        ("collector4", User.Role.COLLECTOR, "Collector Bosco"),
        ("driver1", User.Role.DRIVER, "Driver Muhire"),
        ("driver2", User.Role.DRIVER, "Driver Gakuru"),
        ("sorting1", User.Role.SORTING_STAFF, "Sorter Aline"),
    ]

    for uname, role, full_name in roles_to_create:
        if not User.objects.filter(username=uname).exists():
            lat, lon = get_random_kigali_coords()
            u = User.objects.create_user(uname, f"{uname}@agruni.rw", "password123", role=role)
            u.first_name = full_name
            u.latitude = lat
            u.longitude = lon
            u.save()

    # 4. Customers
    for i in range(1, 21):
        c_uname = f"customer{i}"
        if not User.objects.filter(username=c_uname).exists():
            lat, lon = get_random_kigali_coords()
            customer = User.objects.create_user(c_uname, f"{c_uname}@gmail.com", "password123", role=User.Role.CUSTOMER)
            customer.latitude = lat
            customer.longitude = lon
            customer.save()

    print(f"Population complete. Total users: {User.objects.count()}")

if __name__ == "__main__":
    populate()
