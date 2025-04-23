#!/usr/bin/env python3
"""
Simple utility to check WhatsApp connection status.
"""

import sys
from whatsapp import check_connection

def main():
    """
    Check WhatsApp connection status and report result.
    """
    print("Checking WhatsApp connection...")
    connected, status = check_connection()
    
    if connected:
        print("✅ SUCCESS: WhatsApp is connected and ready to send messages!")
        sys.exit(0)
    else:
        print(f"ERROR: WhatsApp is not connected - {status}")
        print("\nTo reconnect WhatsApp:")
        print("1. Open the web interface at http://localhost:3000/whatsapp")
        print("2. Scan the QR code with your phone")
        print("3. Try running this check again to verify connection")
        sys.exit(1)

if __name__ == "__main__":
    main() 