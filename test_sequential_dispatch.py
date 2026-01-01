#!/usr/bin/env python
import os
import sys
import django
from django.utils import timezone

# --- DYNAMIC PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Point to the 'backend' folder so Python can see 'reikeke_backend'
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

sys.path.insert(0, BACKEND_DIR)
# Also point to 'core' so it can find 'rides', 'accounts' directly
sys.path.insert(0, os.path.join(BACKEND_DIR, 'reikeke_backend', 'core'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Initialize Django
try:
    django.setup()
    print("✅ Django environment initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize Django: {e}")
    sys.exit(1)

# Now we can safely import your models
from rides.models import RideRequest, Location
from accounts.models import User
from locations.models import DriverLocation

def test_sequential_dispatch_logic():
    """Test the sequential dispatch logic"""

    print("\nCreating test data...")
    print("=" * 50)

    try:
        # 1. CLEANUP PREVIOUS TEST DATA (To avoid Duplicate Key errors)
        User.objects.filter(phone_number__in=['08012345678', '08098765432', '08055555555']).delete()

        # 2. CREATE TEST PASSENGER
        passenger = User.objects.create_user(
            phone_number='08012345678',
            password='testpass123',
            user_type=User.UserType.PASSENGER,
            first_name='Test',
            last_name='Passenger'
        )
        print(f"✅ Created passenger: {passenger.phone_number}")

        # 3. CREATE TEST DRIVERS
        drivers = []
        driver_configs = [
            {'phone': '08098765432', 'lat': 6.5244, 'lng': 3.3792},
            {'phone': '08055555555', 'lat': 6.5250, 'lng': 3.3800}
        ]

        for i, config in enumerate(driver_configs, 1):
            driver = User.objects.create_user(
                phone_number=config['phone'],
                password='testpass123',
                user_type=User.UserType.DRIVER,
                is_active=True,
                is_online=True,
                # Add these required fields:
                driver_license_number=f'KD-LICENSE-{i}',
                vehicle_registration=f'JIMETA-KEKE-{i}',
                vehicle_type='keke' 
            )
            DriverLocation.objects.create(
                driver=driver,
                lat=config['lat'],
                lng=config['lng'],
                updated_at=timezone.now()
            )
            drivers.append(driver)
            print(f"✅ Created driver {i}: {driver.phone_number}")
        # 4. CREATE LOCATIONS & RIDE
        pickup = Location.objects.create(address='Main Market', latitude=6.5244, longitude=3.3792)
        dropoff = Location.objects.create(address='Post Office', latitude=6.5300, longitude=3.3850)
        
        ride_request = RideRequest.objects.create(
            passenger=passenger,
            pickup_location=pickup,
            dropoff_location=dropoff,
            status=RideRequest.Status.PENDING,
            base_fare=500.00,
            total_fare=1500.00,
            distance=10.00
        )
        print(f"✅ Created ride request ID: {ride_request.id}")

        print("\nTesting dispatch engine...")
        print("=" * 50)

        # 5. TEST FINDING DRIVERS
        found_drivers = ride_request.find_nearby_active_drivers()
        print(f"1. Drivers found in radius: {found_drivers}")

        if not found_drivers:
            print("❌ No drivers found nearby. Check radius or coordinates.")
            return False

        # 6. TEST ENGINE START
        print("2. Starting engine (triggers first offer)...")
        ride_request.start_sequential_dispatch_engine()
        
        # 7. TEST MOVE TO NEXT
        print("3. Simulating timeout/rejection (moving to next driver)...")
        has_more = ride_request.move_to_next_driver()
        print(f"   More drivers available? {has_more}")
        print(f"   Current driver index is now: {ride_request.current_driver_index}")

        print("\n🎉 ALL LOGIC TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_sequential_dispatch_logic()