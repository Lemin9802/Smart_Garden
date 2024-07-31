import RPi.GPIO as GPIO
import time
import Adafruit_DHT  # Thêm dòng này để nhập module Adafruit_DHT

# Khởi tạo các hằng số
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 0
MOISTURE_PIN = 0
SERVO_PIN = 3

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(MOISTURE_PIN, GPIO.IN)

# Hàm để đọc dữ liệu từ cảm biến DHT11
def read_dht_sensor():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is None or temperature is None:
            raise ValueError("Failed to get reading from sensor")
        return temperature, humidity
    except Exception as e:
        print(f"Error reading DHT sensor: {e}")
        return None, None

# Hàm để đọc dữ liệu từ cảm biến độ ẩm đất
def read_moisture_sensor():
    return GPIO.input(MOISTURE_PIN)

# Hàm để điều khiển servo motor
def rotate_servo(angle):
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(0)
    duty_cycle = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)
    pwm.stop()

# Hàm để dọn dẹp GPIO
def cleanup():
    GPIO.cleanup()
