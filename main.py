import asyncio
import websockets
import json
import spidev
import time
import RPi.GPIO as GPIO

# Set up SPI
spi = spidev.SpiDev()
spi.open(0,0)  # Open SPI bus

# Set GPIO pin for pump
pump = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(pump, GPIO.OUT)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def read_channel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

min_moisture = 500  # Initial default values
max_moisture = 1000

async def send_data(websocket, path):
    global min_moisture, max_moisture

    while True:
        # Check for new settings from the client
        try:
            data = await asyncio.wait_for(websocket.recv(), timeout=1.0)
            settings = json.loads(data)
            min_moisture = int(settings.get('min_moisture', min_moisture))
            max_moisture = int(settings.get('max_moisture', max_moisture))
        except asyncio.TimeoutError:
            # No new data from client, continue
            pass

        moisture_level = read_channel(7)
        timestamp = time.time()

        # Print the current moisture level
        print(f"{timestamp}: Current moisture level: {moisture_level}")

        if moisture_level < min_moisture:  # Check if the soil is dry
            print("Soil dry, watering")
            GPIO.output(pump, GPIO.HIGH)  # Activate the water pump
            time.sleep(10)  # Water for 10 seconds
            GPIO.output(pump, GPIO.LOW)  # Deactivate the water pump
        elif moisture_level > max_moisture:  # Check if the soil is too wet
            print("Soil wet, not watering")
            GPIO.output(pump, GPIO.LOW)  # Ensure the water pump is deactivated

        data = {
            'timestamp': timestamp,
            'moisture_level': moisture_level,
            'min_moisture': min_moisture,
            'max_moisture': max_moisture
        }

        await websocket.send(json.dumps(data))
        await asyncio.sleep(10)


start_server = websockets.serve(send_data, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()