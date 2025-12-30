#!/bin/bash
echo "🚀 Setting up Reikeke USB + NSD Development"

# Check ADB
if ! adb devices | grep -q "device$"; then
    echo "❌ No Android device connected"
    exit 1
fi

# Setup USB networking
echo "🔌 Setting up ADB reverse proxy..."
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000

echo "✅ USB setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Terminal 1: Start backend server"
echo "   cd backend/reikeke_backend/core"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "2. Terminal 2: Start service discovery"
echo "   cd backend/reikeke_backend/core"
echo "   python manage.py service_discovery"
echo ""
echo "3. Terminal 3: Start React Native"
echo "   cd reikeke"
echo "   npm start"
echo ""
echo "4. Terminal 4: Build on Android device"
echo "   cd reikeke"
echo "   expo run:android --device"
echo ""
echo "🎉 Everything will connect automatically!"
