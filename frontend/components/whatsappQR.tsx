// app/components/WhatsAppQR.tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

export default function WhatsAppQR() {
  const [qrState, setQrState] = useState<{
    success: boolean;
    status?: 'connected' | 'qrcode' | 'disconnected' | 'needs_qr' | 'error';
    qrcode?: string;
    message?: string;
  }>({ success: false });

  const [lastStatus, setLastStatus] = useState<string | undefined>(undefined);

  useEffect(() => {
    const fetchQR = async () => {
      try {
        // Add cache-busting parameter to avoid cached responses
        const response = await fetch(`/api/whatsapp-qr?t=${Date.now()}`);
        const data = await response.json();
        console.log('WhatsApp status1:', data);

        // Store previous status for transition notifications
        if (data.status && data.status !== qrState.status) {
          setLastStatus(qrState.status);
        }

        setQrState(data);
      } catch (error) {
        console.error('Error fetching QR code:', error);
        setQrState({
          success: false,
          status: 'error',
          message: error instanceof Error ? error.message : 'Failed to fetch QR code'
        });
      }
    };

    // Initial fetch
    fetchQR();

    // Set up polling with more frequent checks for the "needs_qr" state
    const interval = setInterval(() => {
      fetchQR();
    }, qrState.status === 'needs_qr' ? 1500 : 3000);

    return () => clearInterval(interval);
  }, [qrState.status]);

  // Status transition notification
  useEffect(() => {
    // Only attempt notifications if the browser supports them
    if (typeof window !== 'undefined' && 'Notification' in window) {
      try {
        if (lastStatus === 'connected' && qrState.status !== 'connected') {
          // Device was disconnected - notify user
          if (Notification.permission === 'granted') {
            new Notification('WhatsApp Disconnected', {
              body: 'Your WhatsApp session has ended. A new QR code will be generated automatically.'
            });
          }
        } else if (lastStatus !== 'connected' && qrState.status === 'connected') {
          // Device just connected - notify user
          if (Notification.permission === 'granted') {
            new Notification('WhatsApp Connected', {
              body: 'Your WhatsApp session is now active.'
            });
          }
        }
      } catch (error) {
        console.error('Error showing notification:', error);
      }
    }
  }, [lastStatus, qrState.status]);

  if (!qrState.success && qrState.status !== 'needs_qr' && qrState.status !== 'error') {
    return (
      <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Connecting to WhatsApp</h3>
        <div className="w-12 h-12 border-t-2 border-b-2 border-blue-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (qrState.status === 'connected') {
    return (
      <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
        <h3 className="mb-4 text-lg font-semibold text-green-800">WhatsApp Connected</h3>
        <p className="text-gray-600 mb-4">You are now connected to WhatsApp!</p>
        <div className="w-8 h-8 bg-green-500 rounded-full"></div>
      </div>
    );
  }

  if (qrState.status === 'needs_qr') {
    return (
      <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
        <h3 className="mb-4 text-lg font-semibold text-yellow-800">WhatsApp Session Ended</h3>
        <p className="text-gray-600 mb-4">Generating a new QR code to reconnect...</p>
        <div className="w-12 h-12 border-t-2 border-b-2 border-yellow-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (qrState.status === 'error') {
    return (
      <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
        <h3 className="mb-4 text-lg font-semibold text-red-800">Connection Error</h3>
        <p className="text-gray-600 mb-4">{qrState.message || "Error reconnecting to WhatsApp. The server may need to be restarted."}</p>
        <div className="w-8 h-8 bg-red-500 rounded-full"></div>
      </div>
    );
  }

  if (qrState.status === 'disconnected') {
    return (
      <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">WhatsApp Disconnected</h3>
        <p className="text-gray-600 mb-4">Your WhatsApp session has ended. Waiting for a new QR code...</p>
        <div className="w-12 h-12 border-t-2 border-b-2 border-yellow-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center p-6 bg-white rounded-lg shadow">
      <h3 className="mb-4 text-lg font-semibold text-gray-800">Scan with WhatsApp to Connect</h3>
      {qrState.qrcode && (
        <Image
          src={`data:image/png;base64,${qrState.qrcode}`}
          alt="WhatsApp QR Code"
          width={256}
          height={256}
          unoptimized
        />
      )}
      <p className="text-gray-600 mt-4">Open WhatsApp on your phone and scan this QR code to login</p>
    </div>
  );
}