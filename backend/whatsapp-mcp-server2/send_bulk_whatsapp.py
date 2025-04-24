import sys
import os
import pandas as pd
import argparse
import re
from whatsapp import send_message as whatsapp_send_message
from whatsapp import check_connection
import random
import time
import requests
import datetime
import subprocess
import glob
from typing import List, Tuple

# Fixed message templates that will be slightly varied
MESSAGE_TEMPLATES = [
    """Hey Future Stars!
Want to boost your Math skills while learning the beautiful art of Classical Kathak Dance – all from the comfort of your home?
Here's your chance!
Join the Free Online Classical Kathak Dance + Mathematics Course
by The Art of Living Foundation 
Time: Thrice / week at 6:30 PM
Where: Zoom
Fees: Absolutely FREE!
Why Should You Join?
✅ Fun & Easy Learning
✅ Stronger Math Skills
✅ National Competition Opportunities
✅ Certificates & Government Recognition
✅ Taught by National Awardee Trainers
Ready to shine?
Join the WhatsApp group NOW to get started:
https://chat.whatsapp.com/I5luuVBs7WK7AcOGkne2X6
Watch our Youtube Video Links To see how Thousands of Youth Are Benefiting : 
https://youtu.be/oCGeNckQiIo?si=kpkwqfo2NWsNMR6s
https://youtu.be/5WVWPFCfqs0?si=q631VglxFa8dt0rS
https://youtu.be/o8gmEGFjeVo?si=-GoJKrTjHkFEIz77
Need Help? Call/WhatsApp Us:
📞 9353173653 / 9830059978
Let's learn, dance, and grow together – India is rising!""",

    """Hello Future Stars!
Looking to enhance your Math skills while learning the beautiful art of Classical Kathak Dance? All from home?
Here's your opportunity!
Join the Free Online Classical Kathak Dance + Mathematics Course
by The Art of Living Foundation 
Time: Thrice / week at 6:30 PM
Where: Zoom
Fees: Absolutely FREE!
Benefits:
✅ Fun & Easy Learning
✅ Stronger Math Skills
✅ National Competition Opportunities
✅ Certificates & Government Recognition
✅ Taught by National Awardee Trainers
Want to join?
Join our WhatsApp group to get started:
https://chat.whatsapp.com/I5luuVBs7WK7AcOGkne2X6
Check out our Youtube Videos showing how Thousands of Youth Are Benefiting: 
https://youtu.be/oCGeNckQiIo?si=kpkwqfo2NWsNMR6s
https://youtu.be/5WVWPFCfqs0?si=q631VglxFa8dt0rS
https://youtu.be/o8gmEGFjeVo?si=-GoJKrTjHkFEIz77
Questions? Call/WhatsApp:
📞 9353173653 / 9830059978
Learn, dance, and grow together – India is rising!"""
]

# Greeting variations
GREETINGS = [
    "Hey", "Hello", "Hi", "Greetings", "Namaste", "Good day"
]

# Different emoji variations
EMOJIS = {
    "tick": ["✅", "☑️", "🟢"],
    "phone": ["📞", "📱", "☎️", "📲"],
    "star": ["⭐", "🌟", "✨", "💫"]
}

def format_message_with_links(message):
    """Format the message to ensure links are clickable in WhatsApp."""
    # More comprehensive regex for detecting URLs
    # This will catch various domain formats like youtu.be, example.com, etc.
    url_patterns = [
        # URLs with protocols
        r'(https?:\/\/(?:www\.)?[^\s]+)',
        # URLs starting with www
        r'(?<!\S)(www\.[^\s]+)',
        # Common domain patterns
        r'(?<!\S)([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9]{2,}(?:\.[a-zA-Z0-9]{2,})?(?:\/[^\s\(\)\[\]]*)?)'
    ]
    
    # Combine all patterns
    combined_pattern = '|'.join(url_patterns)
    
    # Find all URLs
    urls = re.findall(combined_pattern, message)
    
    # Flatten the list if it's nested due to capture groups
    flat_urls = []
    for u in urls:
        if isinstance(u, tuple):
            flat_urls.extend([x for x in u if x])
        else:
            flat_urls.append(u)
    
    # Process each URL
    for url in flat_urls:
        if url and not url.startswith(('http://', 'https://')):
            prefixed_url = 'https://' + url
            # Using word boundaries for more precise replacement
            message = re.sub(r'\b' + re.escape(url) + r'\b', prefixed_url, message)
    
    # Special handling for YouTube short links
    youtube_pattern = r'(?<!\S)(youtu\.be\/[^\s]+)'
    youtube_links = re.findall(youtube_pattern, message)
    for link in youtube_links:
        if not link.startswith(('http://', 'https://')):
            prefixed_link = 'https://' + link
            message = re.sub(r'\b' + re.escape(link) + r'\b', prefixed_link, message)
    
    # Special handling for WhatsApp group links
    whatsapp_pattern = r'(?<!\S)(chat\.whatsapp\.com\/[^\s]+)'
    whatsapp_links = re.findall(whatsapp_pattern, message)
    for link in whatsapp_links:
        if not link.startswith(('http://', 'https://')):
            prefixed_link = 'https://' + link
            message = re.sub(r'\b' + re.escape(link) + r'\b', prefixed_link, message)
    
    return message

def personalize_message(base_message, contact_number=None):
    """Add small variations to make messages look manually typed while preserving links"""
    # First identify all links to protect them
    url_patterns = [
        r'(https?:\/\/(?:www\.)?[^\s]+)',
        r'(?<!\S)(www\.[^\s]+)',
        r'(?<!\S)(chat\.whatsapp\.com\/[^\s]+)',
        r'(?<!\S)(youtu\.be\/[^\s]+)'
    ]
    
    # Combine patterns and find all URLs
    combined_pattern = '|'.join(url_patterns)
    urls = re.findall(combined_pattern, base_message)
    
    # Flatten the list of URLs
    flat_urls = []
    for u in urls:
        if isinstance(u, tuple):
            flat_urls.extend([x for x in u if x])
        else:
            flat_urls.append(u)
    
    # Create placeholders for each URL to protect them during modifications
    url_placeholders = {}
    for i, url in enumerate(flat_urls):
        if url:
            placeholder = f"__URL_PLACEHOLDER_{i}__"
            url_placeholders[placeholder] = url
            base_message = base_message.replace(url, placeholder)
    
    # Choose random greeting
    greeting = random.choice(GREETINGS)
    
    # Replace emojis randomly
    for emoji_type, variations in EMOJIS.items():
        if emoji_type == "tick" and "✅" in base_message:
            base_message = base_message.replace("✅", random.choice(variations))
        elif emoji_type == "phone" and "📞" in base_message:
            base_message = base_message.replace("📞", random.choice(variations))
    
    # Add slight typos and corrections occasionally (20% chance)
    if random.random() < 0.2:
        typo_spots = [
            ("boost", "bosot", "boost*"),
            ("learning", "leanring", "learning*"),
            ("Classical", "Clasical", "Classical*"),
            ("Foundation", "Foundaton", "Foundation*"),
            ("skills", "skilsl", "skills*"),
            ("beautiful", "beutiful", "beautiful*"),
            ("opportunity", "oportunity", "opportunity*"),
            ("Benefits", "Benifits", "Benefits*")
        ]
        typo_spot = random.choice(typo_spots)
        if typo_spot[0] in base_message and random.random() < 0.5:
            # Make sure not to replace within a placeholder
            for part in base_message.split():
                if typo_spot[0] in part and not part.startswith("__URL_PLACEHOLDER_"):
                    base_message = base_message.replace(part, part.replace(typo_spot[0], typo_spot[1]), 1)
                    break
            
            # 50% chance to "correct" the typo
            if random.random() < 0.5:
                for part in base_message.split():
                    if typo_spot[1] in part and not part.startswith("__URL_PLACEHOLDER_"):
                        base_message = base_message.replace(part, part.replace(typo_spot[1], typo_spot[2]), 1)
                        break
    
    # Add random whitespace variations (10% chance)
    if random.random() < 0.1:
        lines = base_message.split("\n")
        # Insert an extra blank line at a random position
        insert_pos = random.randint(0, len(lines)-1)
        lines.insert(insert_pos, "")
        base_message = "\n".join(lines)
    
    # Occasionally add personalized intro (15% chance)
    if random.random() < 0.15 and contact_number:
        last_digits = contact_number[-4:]
        intro_lines = [
            f"Hi! Sharing an opportunity with you.",
            f"Hello from The Art of Living Foundation!",
            f"Special invitation for you.",
            f"Sharing something exciting with you today."
        ]
        base_message = random.choice(intro_lines) + "\n\n" + base_message
    
    # Occasionally add a timestamp (10% chance)
    if random.random() < 0.1:
        now = datetime.datetime.now()
        time_msg = f"\n\nSent: {now.strftime('%d/%m/%Y')}"
        base_message += time_msg
    
    # Restore all URL placeholders back to their original URLs
    for placeholder, url in url_placeholders.items():
        base_message = base_message.replace(placeholder, url)
        
    return base_message

def send_image_with_caption(recipient: str, caption: str, image_path: str) -> Tuple[bool, str]:
    """Send an image with a caption to the specified recipient."""
    try:
        # Verify image exists
        if not os.path.exists(image_path):
            return False, f"Image file not found at {image_path}"
            
        # Get absolute paths for everything
        abs_image_path = os.path.abspath(image_path)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        whatsapp_bridge_dir = os.path.abspath(os.path.join(script_dir, "..", "whatsapp-bridge"))
        go_script_path = os.path.join(whatsapp_bridge_dir, "send_whatsapp_image.go")
        
        if not os.path.exists(go_script_path):
            return False, f"Image sending script not found at {go_script_path}"
        
        print(f"Using Go script at: {go_script_path}")
        print(f"Using image at: {abs_image_path}")
        
        # Save current directory
        original_dir = os.getcwd()
        temp_file = None
        
        try:
            # Create a temporary file for the caption to avoid encoding issues
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt')
            temp_file.write(caption)
            temp_file.close()
            caption_file_path = temp_file.name
            print(f"Saved caption to temp file: {caption_file_path}")
            
            # Change to the whatsapp-bridge directory where the Go script and go.mod are
            os.chdir(whatsapp_bridge_dir)
            print(f"Changed to directory: {whatsapp_bridge_dir}")
            
            # Run the Go script with file input for caption
            env = os.environ.copy()
            env['CGO_ENABLED'] = '1'
            cmd = ["go", "run", "send_whatsapp_image.go", recipient, f"file:{caption_file_path}", abs_image_path]
            print(f"Running command: {cmd}")  # Don't join strings to avoid encoding issues
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
            
            # Print output safely, handling encoding issues
            try:
                print(f"Command stdout: {result.stdout}")
                print(f"Command stderr: {result.stderr}")
            except UnicodeEncodeError:
                print("Command output contains characters that can't be displayed in the current console encoding")
                print("Command stderr:", result.stderr.encode('ascii', 'replace').decode('ascii'))
            
            # Check the result
            if result.returncode == 0 and "Image message sent successfully" in result.stdout:
                return True, f"Image sent to {recipient}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Failed to send image: {error_msg}"
                
        finally:
            # Return to original directory
            os.chdir(original_dir)
            # Clean up temp file
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            
    except Exception as e:
        import traceback
        print(f"Exception: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False, f"Error sending image: {str(e)}"

def ensure_clickable_links_in_caption(caption: str) -> str:
    """Format caption to ensure links are clickable when sent with images.
    
    Args:
        caption: The caption text with links
        
    Returns:
        Formatted caption with links that will be clickable on mobile
    """
    # Find all URLs in the caption
    url_patterns = [
        r'https?:\/\/(?:www\.)?[^\s]+',
        r'(?<!\S)www\.[^\s]+',
        r'(?<!\S)chat\.whatsapp\.com\/[^\s]+',
        r'(?<!\S)youtu\.be\/[^\s]+'
    ]
    
    combined_pattern = '|'.join(url_patterns)
    urls = re.findall(combined_pattern, caption)
    
    # For each URL, ensure it's on its own line for better clickability
    modified_caption = caption
    for url in urls:
        # Check if the URL is already on its own line
        url_with_newlines = f"\n{url}\n"
        if url not in modified_caption:
            continue
            
        if f"\n{url}" not in modified_caption and f"{url}\n" not in modified_caption:
            # Replace the URL with a version that has newlines before and after
            modified_caption = modified_caption.replace(url, url_with_newlines)
    
    # Clean up any excessive newlines that might have been created
    modified_caption = re.sub(r'\n{3,}', '\n\n', modified_caption)
    
    return modified_caption

def get_image_files(directory: str) -> List[str]:
    """Get all image files from a directory
    
    Args:
        directory: Path to directory containing images
        
    Returns:
        List of image file paths
    """
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    return image_files

def simulate_human_typing(batch_size, total_contacts):
    """Simulate more human-like messaging patterns"""
    # Real humans don't send at perfectly regular intervals
    current_hour = datetime.datetime.now().hour
    
    # Determine if it's a good time to send messages
    if 22 <= current_hour or current_hour < 7:
        # Late night/early morning - would be suspicious to send many messages
        return min(5, batch_size), True
    elif 9 <= current_hour <= 20:
        # Prime time - can send more messages
        return batch_size, False
    else:
        # Edge times - reduce batch slightly
        return int(batch_size * 0.7), False

def natural_delay_strategy():
    """Create more natural delays between messages"""
    # Base delay that varies with normal human typing patterns
    base_delay = random.uniform(5, 20)  # 5-20 seconds base
    
    # Add random "distractions" that a human might have
    if random.random() < 0.1:  # 10% chance of a "longer distraction"
        return base_delay + random.uniform(30, 120)  # 30s-2m additional delay
    elif random.random() < 0.25:  # 25% chance of a "short pause"
        return base_delay + random.uniform(5, 15)  # 5-15s additional delay
    else:
        return base_delay
        
def send_bulk_messages(excel_path: str, image_dir: str = None, min_delay: int = 5, max_delay: int = 45) -> None:
    """Send WhatsApp message to all numbers in the Excel file with natural delays."""
    try:
        # Simple connection check
        connected, status_msg = check_connection()
        print(f"WhatsApp Status: {'Connected' if connected else 'Disconnected'} - {status_msg}")
        
        # Get absolute path if relative path is provided
        abs_excel_path = os.path.abspath(excel_path)
        
        if not os.path.exists(abs_excel_path):
            print(f"Error: Excel file not found at: {abs_excel_path}")
            return
            
        # Read the Excel file
        df = pd.read_excel(abs_excel_path)
        df = df.dropna(subset=['phone_number'])
        
        if 'phone_number' not in df.columns:
            print("Error: Column 'phone_number' not found in Excel file")
            return
        
        # Shuffle the dataframe to avoid sequential patterns
        df = df.sample(frac=1).reset_index(drop=True)
        
        total = len(df)
        success = 0
        failed = 0
        
        # Check if image mode is enabled
        use_images = False
        available_images = []
        recent_images = []
        
        if image_dir and os.path.exists(image_dir):
            available_images = get_image_files(image_dir)
            if available_images:
                use_images = True
                print(f"Image mode enabled - found {len(available_images)} images in {image_dir}")
                
                # Track recently used images
                max_recent = min(5, len(available_images))
                
                if len(available_images) < 5:
                    print("WARNING: Using fewer than 5 different poster images increases detection risk!")
            else:
                print(f"No images found in {image_dir}, running in text-only mode")
        
        print(f"\nPreparing to send messages to {total} numbers...")
        print(f"Mode: {'Image+Caption' if use_images else 'Text only'}")
        print(f"Using dynamic delay strategy between messages")
        print("-" * 50)
        
        # Process in smaller batches with random sizes
        remaining = total
        processed = 0
        
        while remaining > 0:
            # Determine batch size based on time of day and human patterns
            batch_size, need_long_break = simulate_human_typing(
                min(20, remaining),  # Max 20 per batch
                total
            )
            
            print(f"Processing batch of {batch_size} contacts...")
            
            # Take a subset of the data
            batch = df.iloc[processed:processed+batch_size]
            
            for index, row in batch.iterrows():
                phone = row['phone_number']
                # Clean the phone number
                clean_phone = str(phone).strip().replace("+", "").replace(" ", "").replace("-", "")
                if not clean_phone.startswith("91"):
                    clean_phone = "91" + clean_phone
                
                print(f"Processing: {phone} -> {clean_phone}")
                
                # Choose a message template randomly
                base_template = random.choice(MESSAGE_TEMPLATES)
                
                # Personalize the message
                personalized_message = personalize_message(base_template, clean_phone)
                
                # Format the links
                formatted_message = format_message_with_links(personalized_message)
                
                # Simulate message preparation delay (same for both text and image)
                typing_delay = random.uniform(3, 15)
                print(f"Preparing message... ({typing_delay:.1f}s)")
                time.sleep(typing_delay)
                
                success_status = False
                status_message = ""
                
                # Send with image if in image mode
                if use_images:
                    # Choose image avoiding recently used ones if possible
                    available_choices = [img for img in available_images if img not in recent_images]
                    if not available_choices:
                        # If all images were recently used, reset but avoid the most recent
                        last_used = recent_images[-1] if recent_images else None
                        recent_images = []
                        available_choices = [img for img in available_images if img != last_used]
                    
                    # Select a random image
                    image_path = random.choice(available_choices)
                    
                    # Track for avoiding immediate repetition
                    recent_images.append(image_path)
                    if len(recent_images) > max_recent:
                        recent_images.pop(0)  # Remove oldest
                    
                    print(f"Selected image: {os.path.basename(image_path)}")
                    
                    # Make sure critical URLs are separated to their own lines for better clickability
                    formatted_message = format_message_with_links(personalized_message)
                    
                    # Send the image with caption
                    success_status, status_message = send_image_with_caption(
                        clean_phone, 
                        formatted_message, 
                        image_path
                    )
                    
                    # If image sending fails, fall back to text-only
                    if not success_status:
                        print(f"Image sending failed: {status_message}")
                        print("Falling back to text-only message...")
                        success_status, status_message = whatsapp_send_message(clean_phone, formatted_message)
                else:
                    # Text-only mode
                    success_status, status_message = whatsapp_send_message(clean_phone, formatted_message)
                
                if success_status:
                    mode = "Image+Caption" if use_images else "Text"
                    print(f"SUCCESS: {mode} sent to {clean_phone}: {status_message}")
                    success += 1
                else:
                    print(f"FAILED: Message to {clean_phone}: {status_message}")
                    failed += 1
                
                sys.stdout.flush()
                
                # Add natural delay between messages
                if index < len(batch) - 1:
                    delay = natural_delay_strategy()
                    print(f"Waiting {delay:.1f} seconds before next message...")
                    time.sleep(delay)
            
            processed += batch_size
            remaining -= batch_size
            
            # Take longer breaks between batches
            if remaining > 0:
                # If it's late night or we need a longer break
                if need_long_break:
                    long_break = random.uniform(10*60, 30*60)  # 10-30 minute break
                    print(f"\nTaking a longer break ({long_break/60:.1f} minutes)...")
                    time.sleep(long_break)
                else:
                    batch_break = random.uniform(60, 5*60)  # 1-5 minute break
                    print(f"\nFinished batch - taking a {batch_break/60:.1f} minute break...")
                    time.sleep(batch_break)
        
        print("-" * 50)
        print(f"Summary: Total={total}, Success={success}, Failed={failed}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Send WhatsApp messages in bulk')
    parser.add_argument('excel_path', help='Path to Excel file with phone numbers')
    
    # Keep these arguments for backward compatibility, but they'll be ignored
    message_group = parser.add_mutually_exclusive_group()
    message_group.add_argument('--message', help='Message text to send (will be ignored, template messages are used)')
    message_group.add_argument('--message-file', help='Path to file containing message text (will be ignored, template messages are used)')
    
    # Add image directory parameter
    parser.add_argument('--image-dir', help='Directory containing images to send with captions')
    
    parser.add_argument('--min-delay', type=int, default=5, help='Minimum delay in seconds between messages (default: 5)')
    parser.add_argument('--max-delay', type=int, default=45, help='Maximum delay in seconds between messages (default: 45)')
    parser.add_argument('--stealth-mode', action='store_true', help='Enable maximum stealth mode with more human-like patterns')
    
    args = parser.parse_args()
    
    # Use the enhanced bulk message sender
    send_bulk_messages(args.excel_path, args.image_dir, args.min_delay, args.max_delay)

if __name__ == "__main__":
    main() 