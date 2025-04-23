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
    """Add small variations to make messages look manually typed"""
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
            ("Foundation", "Foundaton", "Foundation*")
        ]
        typo_spot = random.choice(typo_spots)
        if typo_spot[0] in base_message and random.random() < 0.5:
            base_message = base_message.replace(typo_spot[0], typo_spot[1], 1)
            # 50% chance to "correct" the typo
            if random.random() < 0.5:
                base_message = base_message.replace(typo_spot[1], typo_spot[2], 1)
    
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
        
    return base_message

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
        
def send_bulk_messages(excel_path: str, min_delay: int = 5, max_delay: int = 45) -> None:
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
        
        print(f"\nPreparing to send messages to {total} numbers...")
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
                
                # Simulate typing delay before sending
                typing_delay = random.uniform(3, 15)  # 3-15 seconds
                print(f"Preparing message... ({typing_delay:.1f}s)")
                time.sleep(typing_delay)
                
                # Send the message
                success_status, status_message = whatsapp_send_message(clean_phone, formatted_message)
                
                if success_status:
                    print(f"SUCCESS: Message sent to {clean_phone}: {status_message}")
                    success += 1
                else:
                    print(f"FAILED: {clean_phone}: {status_message}")
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
    
    parser.add_argument('--min-delay', type=int, default=5, help='Minimum delay in seconds between messages (default: 5)')
    parser.add_argument('--max-delay', type=int, default=45, help='Maximum delay in seconds between messages (default: 45)')
    parser.add_argument('--stealth-mode', action='store_true', help='Enable maximum stealth mode with more human-like patterns')
    
    args = parser.parse_args()
    
    # Use the enhanced bulk message sender
    send_bulk_messages(args.excel_path, args.min_delay, args.max_delay)

if __name__ == "__main__":
    main() 