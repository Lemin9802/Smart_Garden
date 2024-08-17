import time
from firebase_admin import credentials, initialize_app, db
import grovepi
import RPi.GPIO as GPIO
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import adafruit_dht
import board
import threading
from datetime import datetime

firebase_key_path = '/home/nhatphanh/project/firebase-key.json'

# Initialize Firebase
cred = credentials.Certificate(firebase_key_path)
initialize_app(cred, {
    'databaseURL': 'https://smartgarden-an-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Initialize Firebase Realtime Database reference
ref = db.reference('/sensor_data')

# GPIO configuration
SERVO_PIN = 22  # GPIO pin for the servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
pwm.start(0)

# Initialize DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D17)  # GPIO pin for DHT11 sensor

# Initialize GrovePi
moisture_sensor = 1
motor = 3
grovepi.pinMode(motor, "OUTPUT")
grovepi.pinMode(moisture_sensor, "INPUT")

def set_servo_angle(angle):
    angle = max(0, min(180, angle))
    duty_cycle = (angle / 18.0) + 2.0
    duty_cycle = max(0, min(100, duty_cycle))
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

def read_dht11():
    try:
        humidity = dht_device.humidity
        temperature = dht_device.temperature
        if humidity is not None and temperature is not None:
            print(f"Nhiệt độ: {temperature}°C, Độ ẩm: {humidity}%")  # Print to terminal
            insert_sensor_data(temperature, humidity, 0)  # Assuming soil_moisture = 0
            return humidity, temperature
        else:
            return None, None
    except RuntimeError as error:
        print(f"Lỗi đọc DHT11: {error}")
        return None, None

def insert_sensor_data(temperature, humidity, soil_moisture):
    ref.push({
        'temperature': temperature,
        'humidity': humidity,
        'soil_moisture': soil_moisture,
        'timestamp': datetime.now().isoformat()
    })

def get_sensor_data_from_db():
    all_data = ref.get()
    all_data_list = []
    for key, value in all_data.items():
        all_data_list.append(value)
    return all_data_list

def read_soil_moisture():
    try:
        value = grovepi.analogRead(moisture_sensor)
        # Kiểm tra giá trị trả về là một số nguyên và hợp lệ
        if isinstance(value, int):
            return value
        else:
            print("Giá trị đọc từ cảm biến không hợp lệ")
            return None
    except IOError:
        print("Lỗi khi đọc giá trị từ cảm biến độ ẩm đất")
        return None


def update_dashboard():
    while True:
        humidity, temperature = read_dht11()
        soil_moisture = read_soil_moisture()
        insert_sensor_data(temperature, humidity, soil_moisture)
        time.sleep(10)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Smart Garden Dashboard"),
    dcc.Graph(id='temperature-graph'),
    dcc.Graph(id='humidity-graph'),
    dcc.Graph(id='soil-moisture-graph'),
    html.Button("Open Gate", id='open-gate-btn'),
    html.Button("Close Gate", id='close-gate-btn')
])

@app.callback(
    Output('temperature-graph', 'figure'),
    Output('humidity-graph', 'figure'),
    Output('soil-moisture-graph', 'figure'),
    Input('open-gate-btn', 'n_clicks'),
    Input('close-gate-btn', 'n_clicks')
)
def update_graphs(open_gate, close_gate):
    data = get_sensor_data_from_db()
    temperatures = [item['temperature'] for item in data]
    humidities = [item['humidity'] for item in data]
    soil_moistures = [item['soil_moisture'] for item in data]
    timestamps = [item['timestamp'] for item in data]

    temperature_trace = go.Scatter(x=timestamps, y=temperatures, mode='lines+markers', name='Temperature')
    humidity_trace = go.Scatter(x=timestamps, y=humidities, mode='lines+markers', name='Humidity')
    soil_moisture_trace = go.Scatter(x=timestamps, y=soil_moistures, mode='lines+markers', name='Soil Moisture')

    temperature_figure = {
        'data': [temperature_trace],
        'layout': go.Layout(title='Temperature Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Temperature (°C)'))
    }
    humidity_figure = {
        'data': [humidity_trace],
        'layout': go.Layout(title='Humidity Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Humidity (%)'))
    }
    soil_moisture_figure = {
        'data': [soil_moisture_trace],
        'layout': go.Layout(title='Soil Moisture Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Soil Moisture'))
    }

    if open_gate is not None:
        set_servo_angle(90)
        time.sleep(5)
        set_servo_angle(0)

    if close_gate is not None:
        set_servo_angle(0)

    return temperature_figure, humidity_figure, soil_moisture_figure

if __name__ == '__main__':
    threading.Thread(target=update_dashboard).start()
    app.run_server(debug=True, use_reloader=False)