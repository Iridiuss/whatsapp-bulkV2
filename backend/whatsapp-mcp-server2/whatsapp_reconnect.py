#!/usr/bin/env python3
"""
WhatsApp Connection Manager

This module provides functions to monitor, check, and reconnect the WhatsApp API service.
"""

import os
import time
import subprocess
import requests
import signal
import sys
from typing import Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("whatsapp_reconnect.log")
    ]
)

logger = logging.getLogger("whatsapp_reconnect")

# Constants
WHATSAPP_API_BASE_URL = "http://localhost:9090/api"
WHATSAPP_BRIDGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'whatsapp-bridge')
CONNECTED_FILE = os.path.join(WHATSAPP_BRIDGE_PATH, 'whatsapp_connected.txt')
QR_FILE = os.path.join(WHATSAPP_BRIDGE_PATH, 'latest_qr.txt')

def check_connection() -> Tuple[bool, str]:
    """Check if WhatsApp is connected and return status.
    
    Returns:
        tuple: (connected status boolean, status message string)
    """
    try:
        # Use the QR code endpoint which returns connection status
        response = requests.get(f"{WHATSAPP_API_BASE_URL}/qrcode")
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            message = data.get("message", "")
            
            if status == "connected":
                return True, "Connected to WhatsApp"
            elif status == "qrcode":
                return False, "QR code available for scanning"
            elif status == "needs_qr":
                return False, "Waiting for QR code generation"
            else:
                return False, f"Status: {status} - {message}"
        else:
            return False, f"Error: HTTP {response.status_code}"
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Handle command-line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "check": 
            connected, message = check_connection()
            status = "Connected" if connected else "Disconnected"
            print(f"WhatsApp Statusss: {status} - {message}")
            sys.exit(0 if connected else 1)
            
        else:
            print("Unknown command. Available commands: check, reconnect, force, monitor [interval]")
    else:
        # No command provided, show usage
        print("WhatsApp Connection Manager")
        print("Usage: python whatsapp_reconnect.py [command]")
        print("Commands:")
        print("  check     - Check WhatsApp connection status")
        print("  reconnect - Attempt to reconnect WhatsApp")
        print("  force     - Force reconnection by restarting service")
        print("  monitor   - Start connection monitoring")