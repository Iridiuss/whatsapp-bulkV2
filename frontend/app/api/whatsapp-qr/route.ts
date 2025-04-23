//CHANGED1
import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export async function GET() {
    return await new Promise<Response>((resolve) => {
        // Build absolute paths
        const bridgeDir = path.join(process.cwd(), '..', "backend", "whatsapp-bridge"); //production
        console.log('Bridge directory:', bridgeDir);
        const qrFilePath = path.join(bridgeDir, 'latest_qr.txt');
        const connectedFilePath = path.join(bridgeDir, 'whatsapp_connected.txt');

        let isConnected = false;
        // Check if connected file exists - faster than parsing QR data
        if (fs.existsSync(connectedFilePath)) {
            try {
                const connectedData = fs.readFileSync(connectedFilePath, 'utf-8').trim();
                isConnected = connectedData === 'true';
            } catch (err) {
                console.error('Failed to read connected status file:', err);
            }
        }

        // Try reading the latest QR string from file
        let qrData = '';
        let isSpecialStatus = false;

        if (fs.existsSync(qrFilePath)) {
            try {
                qrData = fs.readFileSync(qrFilePath, 'utf-8').trim();
                isSpecialStatus = qrData === 'NEEDS_QR' || qrData === 'ERROR_RECONNECTING';
            } catch (err) {
                console.error('Failed to read QR file:', err);
                return resolve(NextResponse.json({
                    success: false,
                    status: 'error',
                    message: 'Failed to read QR file',
                }, { status: 500 }));
            }
        }

        // Set environment vars for the Go helper
        const env = {
            ...process.env,
            WHATSAPP_QR_DATA: qrData,
            WHATSAPP_LOGGED_IN: isConnected ? 'true' : 'false',
            WHATSAPP_DISCONNECTED: isSpecialStatus ? 'true' : 'false',
        };

        // Execute with timeout to prevent hanging
        const execOptions = {
            cwd: bridgeDir,
            env,
            timeout: 5000, // 5 second timeout
            maxBuffer: 1024 * 500 // Increased buffer size
        };

        // Execute helper script with env containing QR string
        exec(`go run qrcode_helper.go`, execOptions, (error, stdout, stderr) => {
            if (error) {
                console.error('QR Code helper error:', stderr || error.message);
                return resolve(NextResponse.json({
                    success: false,
                    status: 'error',
                    message: stderr || 'Failed to get QR code',
                }, { status: 500 }));
            }

            try {
                const result = JSON.parse(stdout.trim());
                return resolve(NextResponse.json(result));
            } catch (parseError) {
                console.error('Error parsing helper output:', parseError);
                return resolve(NextResponse.json({
                    success: false,
                    status: 'error',
                    message: 'Invalid response from QR code helper',
                }, { status: 500 }));
            }
        });
    });
}

