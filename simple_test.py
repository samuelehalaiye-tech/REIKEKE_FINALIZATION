#!/usr/bin/env python
"""
Simple test to verify the DriverLocationUpdateView fix works correctly
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

# Set up Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reikeke_backend.core.core.settings')

# Setup Django
django.setup()

from accounts.models import User
from locations.models import DriverLocation
from locations.views import DriverLocationUpdateView
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

def test_driver_location_update_view():
    """Test the DriverLocationUpdateView with a new driver"""

    print("Creating test driver user...")
    # Create a test user who is a driver
    driver_user = User.objects.create_user(
        phone_number='08012345678',
        password='testpass123',
        user_type=User.UserType.DRIVER,
        driver_license_number='DRV12345',
        vehicle_registration='LAG123AB',
        vehicle_type='car'
    )
    print(f"✅ Created driver user: {driver_user.phone_number}")

    # Create a mock request
    factory = APIRequestFactory()
    request = factory.put('/api/driver-location/', {'lat': 6.5244, 'lng': 3.3792}, format='json')
    request.user = driver_user

    # Test the view
    view = DriverLocationUpdateView()
    view.request = request

    try:
        print("Testing DriverLocationUpdateView.get_object()...")
        # This should work now - get_or_create should handle the case where no DriverLocation exists
        driver_location = view.get_object()
        print(f"✅ SUCCESS: DriverLocation retrieved/created for driver {driver_user.phone_number}")
        print(f"   DriverLocation ID: {driver_location.id}")
        print(f"   Driver: {driver_location.driver.phone_number}")

        # Verify the record was created in the database
        db_record = DriverLocation.objects.get(driver=driver_user)
        print(f"   Database record exists: {db_record is not None}")

        # Clean up
        driver_location.delete()
        driver_user.delete()

        return True

    except permissions.PermissionDenied as e:
        print(f"❌ PERMISSION ERROR: {e}")
        # Clean up
        driver_user.delete()
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        # Clean up
        driver_user.delete()
        return False

def test_non_driver_user():
    """Test that non-driver users are properly rejected"""

    print("\nCreating test passenger user...")
    # Create a test user who is a passenger
    passenger_user = User.objects.create_user(
        phone_number='08098765432',
        password='testpass123',
        user_type=User.UserType.PASSENGER
    )
    print(f"✅ Created passenger user: {passenger_user.phone_number}")

    # Create a mock request
    factory = APIRequestFactory()
    request = factory.put('/api/driver-location/', {'lat': 6.5244, 'lng': 3.3792}, format='json')
    request.user = passenger_user

    # Test the view
    view = DriverLocationUpdateView()
    view.request = request

    try:
        driver_location = view.get_object()
        print(f"❌ UNEXPECTED SUCCESS: Non-driver user was able to access driver location update")
        # Clean up
        passenger_user.delete()
        return False

    except permissions.PermissionDenied as e:
        print(f"✅ SUCCESS: Non-driver user properly rejected with: {e}")
        # Clean up
        passenger_user.delete()
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        # Clean up
        passenger_user.delete()
        return False

if __name__ == '__main__':
    print("Testing DriverLocationUpdateView fix...")
    print("=" * 50)

    print("Test 1: New driver updating location (should create DriverLocation)")
    test1_result = test_driver_location_update_view()

    print("\nTest 2: Non-driver user trying to update location (should be rejected)")
    test2_result = test_non_driver_user()

    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
