from gpiozero import MotionSensor

# Define three PIR sensors
pir1 = MotionSensor(4)
pir2 = MotionSensor(5)
pir3 = MotionSensor(6)

print("Motion sensors active (GPIO 4, 5, 6). Waiting for motion...")

while True:
    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 4)")
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 5)")
        pir2.wait_for_no_motion()

    if pir3.motion_detected:
        print("Motion detected on PIR 3 (GPIO 6)")
        pir3.wait_for_no_motion()