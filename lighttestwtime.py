from gpiozero import LED
from datetime import datetime
import time

# Define LED on GPIO 27
led = LED(27)

def is_night_time():
    """Return True if current time is after 5 PM or before 9 AM."""
    hour = datetime.now().hour
    return hour >= 17 or hour < 12

print("Testing LED on GPIO 27 with time check...")

try:
    while True:
        if is_night_time():
            print(f"{datetime.now()}: Nighttime detected — LED ON")
            led.on()
            time.sleep(1)
            led.off()
        else:
            print(f"{datetime.now()}: Daytime detected — LED OFF")
            led.off()
        time.sleep(10)  # check every 10 seconds
except KeyboardInterrupt:
    print("Test stopped by user.")
    led.off()
