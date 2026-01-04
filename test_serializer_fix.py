#!/usr/bin/env python3

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

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
            'reikeke_backend.core.rides',
            'reikeke_backend.core.locations',
            'reikeke_backend.core.accounts',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

# Setup Django
django.setup()

# Now we can import Django models
from rides.models import RideRequest, RideOffer, Location
from rides.serializers import RideRequestSerializer, RideDetailSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def test_serializer_fix():
    print("Testing serializer fixes...")

    # Create a test user
    user = User.objects.create_user(
        phone_number='+1234567890',
        password='testpass',
        user_type='passenger'
    )

    # Create test locations
    pickup_location = Location.objects.create(
        latitude=6.5244,
        longitude=3.3792
    )

    dropoff_location = Location.objects.create(
        latitude=6.5250,
        longitude=3.3800
    )

    # Create a test ride request
    ride = RideRequest.objects.create(
        passenger=user,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        status='pending'
    )

    print(f"Created ride: {ride.id}")

    # Test RideRequestSerializer
    serializer = RideRequestSerializer(ride)
    data = serializer.data

    print("RideRequestSerializer data:")
    print(f"  pickup_lat: {data.get('pickup_lat')}")
    print(f"  pickup_lng: {data.get('pickup_lng')}")
    print(f"  dropoff_lat: {data.get('dropoff_lat')}")
    print(f"  dropoff_lng: {data.get('dropoff_lng')}")

    # Verify the coordinates are correctly extracted
    assert data['pickup_lat'] == float(pickup_location.latitude)
    assert data['pickup_lng'] == float(pickup_location.longitude)
    assert data['dropoff_lat'] == float(dropoff_location.latitude)
    assert data['dropoff_lng'] == float(dropoff_location.longitude)

    print("✅ RideRequestSerializer test passed!")

    # Test RideDetailSerializer
    detail_serializer = RideDetailSerializer(ride)
    detail_data = detail_serializer.data

    print("RideDetailSerializer data:")
    print(f"  pickup_lat: {detail_data.get('pickup_lat')}")
    print(f"  pickup_lng: {detail_data.get('pickup_lng')}")
    print(f"  dropoff_lat: {detail_data.get('dropoff_lat')}")
    print(f"  dropoff_lng: {detail_data.get('dropoff_lng')}")

    # Verify the coordinates are correctly extracted
    assert detail_data['pickup_lat'] == float(pickup_location.latitude)
    assert detail_data['pickup_lng'] == float(pickup_location.longitude)
    assert detail_data['dropoff_lat'] == float(dropoff_location.latitude)
    assert detail_data['dropoff_lng'] == float(dropoff_location.longitude)

    print("✅ RideDetailSerializer test passed!")

    # Test driver location access (should return None since no driver assigned)
    driver_location = detail_data.get('driver_location')
    print(f"Driver location (should be None): {driver_location}")
    assert driver_location is None

    print("✅ Driver location test passed!")

    print("🎉 All serializer tests passed!")

if __name__ == '__main__':
    test_serializer_fix()
