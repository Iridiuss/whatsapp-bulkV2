// qrcode_helper.go
package main

import (
	"encoding/base64"
	"fmt"
	"os"
	"runtime/debug"

	"github.com/skip2/go-qrcode"
)

func main() {
	// Force garbage collection before processing
	debug.FreeOSMemory()
	
	// Defer panic recovery
	defer func() {
		if r := recover(); r != nil {
			fmt.Println("{\"success\":false,\"status\":\"error\",\"message\":\"Internal server error generating QR code\"}")
			// Force garbage collection after panic
			debug.FreeOSMemory()
		}
	}()

	// Read QR data from environment
	qrData := os.Getenv("WHATSAPP_QR_DATA")
	
	// Check if we're logged in
	if qrData == "" {
		if os.Getenv("WHATSAPP_LOGGED_IN") == "true" {
			fmt.Println("{\"success\":true,\"status\":\"connected\",\"message\":\"WhatsApp is connected\"}")
		} else if os.Getenv("WHATSAPP_DISCONNECTED") == "true" {
			fmt.Println("{\"success\":false,\"status\":\"disconnected\",\"message\":\"WhatsApp has been disconnected\"}")
		} else {
			fmt.Println("{\"success\":false,\"status\":\"disconnected\",\"message\":\"No QR code available\"}")
		}
		return
	}

	// Handle special status values
	if qrData == "NEEDS_QR" {
		fmt.Println("{\"success\":false,\"status\":\"needs_qr\",\"message\":\"Waiting for QR code...\"}")
		return
	}
	
	if qrData == "ERROR_RECONNECTING" {
		fmt.Println("{\"success\":false,\"status\":\"error\",\"message\":\"Error reconnecting to WhatsApp\"}")
		return
	}

	// Generate smaller QR code (less memory usage)
	qr, err := qrcode.New(qrData, qrcode.Medium)
	if err != nil {
		fmt.Println("{\"success\":false,\"status\":\"error\",\"message\":\"Failed to generate QR code\"}")
		return
	}

	// Create smaller PNG image (152px instead of 256px to reduce memory usage)
	png, err := qr.PNG(152)
	if err != nil {
		fmt.Println("{\"success\":false,\"status\":\"error\",\"message\":\"Failed to create PNG image\"}")
		return
	}

	// Convert to base64 and return simplified JSON
	base64Data := base64.StdEncoding.EncodeToString(png)
	fmt.Printf("{\"success\":true,\"status\":\"qrcode\",\"qrcode\":\"%s\"}\n", base64Data)
	
	// Clean up to avoid memory leaks
	png = nil
	qr = nil
	debug.FreeOSMemory()
}