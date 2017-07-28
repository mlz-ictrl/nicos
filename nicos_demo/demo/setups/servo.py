description = "servos on micropython"
group = "optional"
includes = []

devices = dict(
    io = device('nicos_demo.demo.devices.servo.SerComIO',
                description = "dev for communication",
                devfile = "/dev/ttyACM0",
                lowlevel = True,
               ),

    s1 = device('nicos_demo.demo.devices.servo.MicroPythonServo',
                description = "Servo1",
                io = 'io',
                channel = 1,
                speed = 10,
                unit = "deg",
                abslimits = (-90, 90),
               ),
    s2 = device('nicos_demo.demo.devices.servo.MicroPythonServo',
                description = "Servo2",
                io = 'io',
                channel = 2,
                speed = 10,
                unit = "deg",
                abslimits = (-90, 90),
                offset = -90,
               ),
    s3 = device('nicos_demo.demo.devices.servo.MicroPythonServo',
                description = "Servo3",
                io = 'io',
                channel = 3,
                speed = 10,
                unit = "deg",
                abslimits = (-90, 90),
                offset = 90,
               ),
)
