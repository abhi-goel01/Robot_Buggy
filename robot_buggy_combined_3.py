from gpiozero import Robot, LineSensor, InputDevice, OutputDevice
from time import sleep, time

# Define GPIO pin mapping
trig = OutputDevice(4)
echo = InputDevice(17)
left_sensor = LineSensor(19)
right_sensor= LineSensor(26)
zack = Robot(left=(10,9),right=(7,8))
swap = 1

# Sleep for a couple of seconds to initialize the UDS
sleep(2)

# Define a function to calculate the UDS pulse time
def get_pulse_time():
    pulse_start, pulse_end = 0, 0

    trig.on()
    sleep(0.00001)
    trig.off()

    while echo.is_active == False:
        pulse_start = time()

    while echo.is_active == True:
        pulse_end = time()

    return pulse_end - pulse_start

# Define a function to calculate the distance of obstacle in front of the buggy
def calculate_distance(duration):
    speed = 343
    distance = speed * duration / 2
    # calculate distance in metres
    return distance

# Generator function to run constantly and decide which ways the motors should move
def motor_speed():
    # Define a global variable to alternate the left and right movement when an
    # obstacle is encountered
    global swap
    while True:

        # Detect if the robot has come over the Line
        # When on line then value of the sensor = 1
        left_detect  = int(left_sensor.value)
        right_detect = int(right_sensor.value)

        # If the robot is clear of the line then check for obstacle and move forward accordignly
        if left_detect == 0 and right_detect == 0:
            duration = get_pulse_time()
            distance = calculate_distance(duration)
            if distance < 0.1:
                if swap == 1:
                    zack.left()
                    sleep(1.3)
                    swap = 0
                else:
                    zack.right()
                    sleep(1.3)
                    swap = 1
            else:
                left_motor  = 1
                right_motor = 1

        # If the robot has drifted left then move the robot right
        if right_detect == 1 and left_detect == 0:
            left_motor  = -1
            right_motor = 1

        # If the robot has drifted right then move the robot left
        if left_detect == 1 and right_detect == 0:
            left_motor  = 1
            right_motor = -1

        # If the robot by chance comes at 90 degree with the line then turn right
        if left_detect == 1 and right_detect == 1:
            zack.right()
            sleep(0.8)

        # send the instructions to caller function
        yield(right_motor,left_motor)

zack.source = motor_speed()

# Run the program for n seconds and close the Robot
sleep(100)
zack.stop()
zack.source = None
zack.close()
left_sensor.close()
right_sensor.close()
