# test_dht.py
import adafruit_dht
import board

# Cấu hình GPIO
DHT_PIN = board.D4  # Cập nhật chân GPIO của cảm biến DHT

# Khởi tạo cảm biến DHT
dht_sensor = adafruit_dht.DHT11(DHT_PIN)

try:
    temperature = dht_sensor.temperature
    humidity = dht_sensor.humidity
    print(f"Temperature: {temperature} C")
    print(f"Humidity: {humidity} %")
except Exception as e:
    print(f"Error reading sensor data: {e}")
