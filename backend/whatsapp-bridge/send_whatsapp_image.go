// File: backend/whatsapp-mcp-server2/send_whatsapp_image.go

package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
)

func main() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: go run send_whatsapp_image.go <phone_number> <message> <image_path>")
		os.Exit(1)
	}

	phoneNumber := os.Args[1]
	message := os.Args[2]
	imagePath := os.Args[3]

	fmt.Printf("Sending image to %s with message: %s\n", phoneNumber, message)
	fmt.Printf("Image path: %s\n", imagePath)

	// Verify image exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		fmt.Printf("Error: Image file not found at %s\n", imagePath)
		os.Exit(1)
	}

	// Setup WhatsApp client
	dbDir := filepath.Join("..", "whatsapp-bridge", "store")
	dbPath := filepath.Join(dbDir, "whatsapp.db")
	
	// Ensure the directory exists
	if _, err := os.Stat(dbDir); os.IsNotExist(err) {
		fmt.Printf("Error: Database directory not found at %s\n", dbDir)
		fmt.Println("Make sure the WhatsApp bridge has been run first")
		os.Exit(1)
	}

	// Connect to the database
	logger := waLog.Stdout("Client", "DEBUG", true)
	container, err := sqlstore.New("sqlite3", "file:"+dbPath+"?_foreign_keys=on", logger)
	if err != nil {
		fmt.Printf("Failed to connect to database: %v\n", err)
		os.Exit(1)
	}

	// Get the device
	deviceStore, err := container.GetFirstDevice()
	if err != nil {
		fmt.Printf("Failed to get device: %v\n", err)
		os.Exit(1)
	}

	// Create a new client
	client := whatsmeow.NewClient(deviceStore, logger)
	
	// Check if device is registered
	if client.Store.ID == nil {
		fmt.Println("No WhatsApp account is connected. Please run the WhatsApp bridge and scan the QR code first.")
		os.Exit(1)
	}

	// Connect to WhatsApp
	err = client.Connect()
	if err != nil {
		fmt.Printf("Failed to connect to WhatsApp: %v\n", err)
		os.Exit(1)
	}
	defer client.Disconnect()

	// Wait for connection to establish
	time.Sleep(2 * time.Second)

	if !client.IsConnected() {
		fmt.Println("Failed to establish WhatsApp connection")
		os.Exit(1)
	}

	// Read the image file
	imgData, err := os.ReadFile(imagePath)
	if err != nil {
		fmt.Printf("Failed to read image file: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Image size: %d bytes\n", len(imgData))

	// Create recipient JID
	recipientJID := types.JID{
		User:   phoneNumber,
		Server: "s.whatsapp.net",
	}

	// Upload the image
	fmt.Println("Uploading image to WhatsApp servers...")
	uploadedImage, err := client.Upload(context.Background(), imgData, whatsmeow.MediaImage)
	if err != nil {
		fmt.Printf("Failed to upload image: %v\n", err)
		
		// Try to send text-only message as fallback
		fmt.Println("Trying to send text-only message instead...")
		_, err = client.SendMessage(context.Background(), recipientJID, &waProto.Message{
			Conversation: proto.String(message),
		})
		if err != nil {
			fmt.Printf("Failed to send text message: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("Sent text-only message (image upload failed)")
		os.Exit(0)
	}

	// Create image message
	imageMsg := &waProto.Message{
		ImageMessage: &waProto.ImageMessage{
			Url:           proto.String(uploadedImage.URL),
			Mimetype:      proto.String("image/jpeg"),
			FileLength:    proto.Uint64(uint64(len(imgData))),
			FileSha256:    uploadedImage.FileSHA256,
			FileEncSha256: uploadedImage.FileEncSHA256,
			MediaKey:      uploadedImage.MediaKey,
			Caption:       proto.String(message),
		},
	}

	// Send the message
	fmt.Println("Sending message with image...")
	_, err = client.SendMessage(context.Background(), recipientJID, imageMsg)
	if err != nil {
		fmt.Printf("Failed to send image message: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Image message sent successfully!")
}