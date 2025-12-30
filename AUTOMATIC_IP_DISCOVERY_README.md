# Automatic IP Discovery for Reikeke Development

## Overview
This feature eliminates the need to manually configure IP addresses when switching networks during development. The system uses mDNS/Bonjour service discovery to automatically find and connect to the development server.

## How It Works

### Backend (Django)
1. **Service Advertisement**: The Django server automatically advertises itself on the local network using mDNS/Bonjour
2. **Service Information**: Includes server IP, port, version, and environment details
3. **Continuous Broadcasting**: Runs continuously while the server is active

### Frontend (React Native)
1. **Service Discovery**: Apps scan the local network for available servers
2. **Automatic Connection**: Connects to discovered servers automatically
3. **Persistent Storage**: Remembers the last connected server
4. **Manual Override**: Allows manual server selection if needed

## Setup Instructions

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend/reikeke_backend/core
   pip install zeroconf==0.132.2
   ```

2. **Start Service Discovery**:
   ```bash
   python manage.py service_discovery
   ```

   This will advertise the server at your current IP address on port 8000.

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd reikeke
   npm install react-native-zeroconf@^0.13.8
   ```

2. **Automatic Discovery**:
   The app will automatically discover servers when it starts. The config service loads the last discovered server URL from AsyncStorage.

3. **Manual Discovery** (if needed):
   Use the `ServiceDiscovery` component in your app to manually trigger discovery:
   ```tsx
   import { ServiceDiscovery } from '../components/ServiceDiscovery';

   // In your component
   <ServiceDiscovery onServerFound={(url) => console.log('Connected to:', url)} />
   ```

## Usage

### For Developers

1. **Start Backend**: Run `python manage.py service_discovery` in a separate terminal
2. **Start Frontend**: Run `npm start` as usual
3. **Automatic Connection**: The app will automatically connect to the discovered server
4. **Network Changes**: When you change networks, restart the backend discovery and the app will find the new IP

### For Multiple Developers

- Each developer runs `python manage.py service_discovery` on their machine
- Apps on phones/tablets will discover all available servers
- Developers can choose which server to connect to
- No IP address sharing or manual configuration needed

## Files Modified

### Backend
- `backend/reikeke_backend/core/requirements.txt` - Added zeroconf dependency
- `backend/reikeke_backend/core/core/settings.py` - Added service discovery configuration
- `backend/reikeke_backend/core/core/management/commands/service_discovery.py` - Service advertisement command

### Frontend
- `reikeke/package.json` - Added react-native-zeroconf dependency
- `reikeke/hooks/useServiceDiscovery.ts` - Service discovery hook
- `reikeke/services/config.ts` - Automatic config loading from discovered servers
- `reikeke/components/ServiceDiscovery.tsx` - Manual discovery interface

## Troubleshooting

### Backend Issues
- **Service not advertising**: Check if zeroconf is installed and the command is running
- **Firewall blocking**: Ensure mDNS traffic (port 5353) is allowed
- **Wrong IP detected**: The service automatically detects your local IP

### Frontend Issues
- **No servers found**: Ensure backend is running `service_discovery` command
- **Connection fails**: Check network connectivity and firewall settings
- **Old server remembered**: Clear AsyncStorage or use manual discovery to override

### Network Issues
- **Corporate networks**: May block mDNS traffic - use manual IP configuration
- **VPN interference**: Disable VPN or configure appropriately
- **Multiple interfaces**: Server may advertise on wrong network interface

## Technical Details

### Service Information
- **Service Type**: `_reikeke._tcp.local.`
- **Service Name**: `ReikekeDevServer`
- **Port**: 8000 (configurable)
- **Properties**: version, environment

### Discovery Process
1. Backend advertises service every 30 seconds
2. Frontend scans for 30 seconds on startup
3. First discovered server is automatically selected
4. Selection is persisted in AsyncStorage

### Security Considerations
- Only works on local networks
- No authentication required for discovery
- Development-only feature (disabled in production)

## Future Enhancements

- **QR Code Fallback**: Generate QR codes for manual scanning
- **Development Companion App**: Desktop app to manage server discovery
- **Service Prioritization**: Prefer servers based on version/location
- **Health Checks**: Verify server availability before connecting

---

This feature makes development much smoother by eliminating IP configuration hassles. Just start the backend discovery service and your apps will find the server automatically!
