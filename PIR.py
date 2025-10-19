from gpiozero import MotionSensor
import time

# Define three PIR sensors
pir1 = MotionSensor(21)
pir2 = MotionSensor(24)
pir3 = MotionSensor(25)

print("Motion sensors active (GPIO 21, 24, 25). Waiting for motion...")

while True:
    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 21)")
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 24)")
        pir2.wait_for_no_motion()

    if pir3.motion_detected:
        print("Motion detected on PIR 3 (GPIO 25)")
        pir3.wait_for_no_motion()
    
    time.sleep(0.1)  # small delay prevents deque mutation error