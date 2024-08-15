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

# Firebase configuration
firebase_url = 'https://smartgarden-an-default-rtdb.asia-southeast1.firebasedatabase.app/'
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "smartgarden-an",
    "private_key_id": "9cdd5794583d95a9c648787f1dc84a816d6c4e9d",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDJW40TYcanmzjX\npm/3HN8UBElvcv03rQo0isulJGpDbXoKu+dwJx+GU/9Ra8O6FUuW/MYIG4k2Fazc\nnhVJl/uKfeidpz452hRrS9HfG+DkVpU2e0QxrFHBcJUzu2F4kqL7dnrBYAVyN1V6\npFUpOtv+yWJVay14tajkOZMOQ2pFJjy6UE5lmyxT9hHsBabIShIX6n1ssVMcgww+\nZPtU+NTGPMwngEbw+MFoV2Qj/aDkfC0opX03BFNUSykUOFIBmDEtOsXbNuNVEDsI\n8AOiQrS5U4Poa9JyReouFWn5rrD7BiEC1saa1eV1l1lCLsYs5qTD7oLUNTDUMY1X\nc0YcRtfBAgMBAAECggEANUBVCu8szl6qpb2Kltu3019e3G6YsQS+Ui7ytHXw9Gwb\nfoM7Ldnq6GeGek35sVi4aPHonXRK0VbiJGZaUuAy0emCf08fkcUu6UFf+5Uv4LNV\nOtdWrZxY8sOHcer4WB7Po5kt1b5DMnWX0ZtsOj8qtzMjIlv55paEV/cyAO+rRyXh\nA7DVoS65pSc1HMFIXPo4MteWnncS7M0e/MUgD00DhnHbYt0K339+erpWTQ76AK1B\nSSTNjcwo75tQXPJuYxIJIolgOxLmCetxk3r1iLQaxepLScYBo3aVfBHa4C+I5Fcv\n+G8dAZE7d+xfvn0JUNocjDs1Ni06FbekLKPua8g9EQKBgQD5Wbue9shI9+1ybIOZ\njFtQxk1M+zrrT3y76iUw3AS9dLP3YPDIuEcCxJmT57Vp64xaC+IJTvq2F6DBYmaG\nIWzRFKMtzZwz0moJuVnTJIACr1Y+SvXYE3Fp0zwQENOgJLZK/W0DvoSYF21S1kDu\nsFhBRh34wegvShViOZZF6kJw6wKBgQDOui4ZsNACrKrTySWw2zy5rn5EnmYE9Zzq\nYrj0af1xfBygPdb0uxx5xuID4bD65ETum+A+orWtmyIaxEVPfKuFIbZz4330n6Lk\nObf4EsyCvnerxBS9FMw3Sn5DXpHJ8PTYkTaiajK95qUJoPkC0w9XwjwL2l+sAU+Z\ntoc6dDVPAwKBgESjJrpDRC6R0JLGvBLwR9KcQ3sFTNqpLrSrZ0Fjzwo3rbJSxPT7\nhNCGPaAxEAbwB9phmv7k9q5ZIq8Y3w/c8486FxDsoCrDqNy0YL12NqaGjT7oc3Pf\nJkDzHH1vpFFYybUqvW9iai1ThYxf3c/WSvTs0CNBfSBHTEuVfoAQU+mxAoGAeAuj\ng6WqVTNBi/SNn5LgQ48xodU9tvmN4onrj3sRAtqooODoN3uEgK7eRpTDuh3ebZU0\n9gp0Z9jjSBnbidoCnC/EjK15Uhl1dQSTcUoxWmcShTs7M8WlBSKMCcEb9eGnvS8u\nQ8hZqO8LvXitwVcg3LxdNCDeV7r3J3LYOjiLUFMCgYBNzNaC29dtoTINpn78FreC\n4tdHSn1S+8sxYGfDTGNjD8J8qElKBPAzFSXbqFSDDgHfFW6NlAawbe5kDmznuTzk\nL4VOhNVkj1O8NtRMbYd7UilRd9FhNrQxiTvhmJzvxj2xPX7dN401OJiPS/61PdmK\n5V45BgVTL+Z1xDKtpB4SrA==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-7sfij@smartgarden-an.iam.gserviceaccount.com",
    "client_id": "108343873320027577640",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7sfij%40smartgarden-an.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
initialize_app(cred, {
    'databaseURL': firebase_url
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
    return grovepi.analogRead(moisture_sensor)

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
