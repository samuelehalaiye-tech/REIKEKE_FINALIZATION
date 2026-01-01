#!/usr/bin/env python
"""
Test script to verify the DriverLocationUpdateView fix
This simulates the scenario where a new driver tries to go online
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the Python path
sys.path.insert(0, 'backend')

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
            'reikeke_backend.core.accounts.apps.AccountsConfig',
            'reikeke_backend.core.locations.apps.LocationsConfig',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

# Setup Django
django.setup()

from reikeke_backend.core.accounts.models import User
from reikeke_backend.core.locations.models import DriverLocation
from reikeke_backend.core.locations.views import DriverLocationUpdateView
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

def test_driver_location_update_view():
    """Test the DriverLocationUpdateView with a new driver"""

    # Create a test user who is a driver
    driver_user = User.objects.create_user(
        phone_number='08012345678',
        password='testpass123',
        user_type=User.UserType.DRIVER,
        driver_license_number='DRV12345',
        vehicle_registration='LAG123AB',
        vehicle_type='car'
    )

    # Create a mock request
    factory = APIRequestFactory()
    request = factory.put('/api/driver-location/', {'lat': 6.5244, 'lng': 3.3792}, format='json')
    request.user = driver_user

    # Test the view
    view = DriverLocationUpdateView()
    view.request = request

    try:
        # This should work now - get_or_create should handle the case where no DriverLocation exists
        driver_location = view.get_object()
        print(f"✅ SUCCESS: DriverLocation retrieved/created for driver {driver_user.phone_number}")
        print(f"   DriverLocation ID: {driver_location.id}")
        print(f"   Driver: {driver_location.driver.phone_number}")
        print(f"   Created new record: {not DriverLocation.objects.filter(driver=driver_user).exists() and True}")

        # Verify the record was created in the database
        db_record = DriverLocation.objects.get(driver=driver_user)
        print(f"   Database record exists: {db_record is not None}")

        return True

    except permissions.PermissionDenied as e:
        print(f"❌ PERMISSION ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_non_driver_user():
    """Test that non-driver users are properly rejected"""

    # Create a test user who is a passenger
    passenger_user = User.objects.create_user(
        phone_number='08098765432',
        password='testpass123',
        user_type=User.UserType.PASSENGER
    )

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
        return False

    except permissions.PermissionDenied as e:
        print(f"✅ SUCCESS: Non-driver user properly rejected with: {e}")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == '__main__':
    print("Testing DriverLocationUpdateView fix...")
    print("=" * 50)

    # Run database migrations
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)

    print("Test 1: New driver updating location (should create DriverLocation)")
    test1_result = test_driver_location_update_view()

    print("\nTest 2: Non-driver user trying to update location (should be rejected)")
    test2_result = test_non_driver_user()

    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
