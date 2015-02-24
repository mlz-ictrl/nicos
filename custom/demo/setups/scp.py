description = 'simple communication protocol demo setup'

group = 'optional'

devices = dict(
    ethernetcomm = device('devices.vendor.simplecomm.EthernetCommunicator',
                        lowlevel=True,
                        host='127.0.0.1:14728',
                        timeout=3.0,
                       ),

    serialcomm = device('devices.vendor.simplecomm.SerialCommunicator',
                        lowlevel=True,
                        devfile='/dev/ttyACM0',
                        timeout=3.0,
                       ),

    mockdevice = device('devices.vendor.simplecomm.SimpleCommReadable',
                        description = 'A virtual device for testing',
                        comm = 'ethernetcomm',
                        unit='rpm',
                       ),

    mockmotor = device('devices.vendor.simplecomm.SimpleCommMoveable',
                        description = 'A virtual device simulating a motor',
                        comm = 'ethernetcomm',
                        unit='mm',
                       ),

    servo1 = device('devices.vendor.simplecomm.SimpleCommMoveable',
                        description = 'Servo connected to the X1 pin on the pyboard',
                        comm = 'serialcomm',
                        unit='deg',
                       ),

    servo2 = device('devices.vendor.simplecomm.SimpleCommMoveable',
                        description = 'Servo connected to the X2 pin on the pyboard',
                        comm = 'serialcomm',
                        unit='deg',
                       ),

    servo3 = device('devices.vendor.simplecomm.SimpleCommMoveable',
                        description = 'Servo connected to the X3 pin on the pyboard',
                        comm = 'serialcomm',
                        unit='deg',
                       ),
)

