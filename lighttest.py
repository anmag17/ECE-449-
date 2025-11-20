from gpiozero import LED
import time

# Define LED on GPIO 27
led = LED(16)

print("Testing LED on GPIO 27...")

try:
    while True:
        print("LED ON")
        led.on()
        time.sleep(10)
        print("LED OFF")
        led.off()
        time.sleep(10)

except KeyboardInterrupt:
    print("Test stopped by user.")
    led.off()
