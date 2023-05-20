import socket
import network
from machine import Pin
import dht
import time
import math
import ssd1306
from utime import sleep
import framebuf
from images import (logo)

ssid = 'iPhone (168)'   
password = 'minecraft'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Conexion correcta')
print(station.ifconfig())

#Configuracion de sensores
sensor_temperatura = machine.ADC(26)
dht11Sensor = dht.DHT11(machine.Pin(13, machine.Pin.PULL_UP))
ldr = machine.ADC(27)

def leerFotoResistencia():
    global luz_solar
    rango_bajo = range(0, 30000)
    rango_medio = range(30001, 60000)
    rango_alto = range(60001, 70000)
    valor = ldr.read_u16()
    
    if int(valor) in rango_alto:
        luz_solar = "alta"
    elif int(valor) in rango_medio:
        luz_solar = "media"
    elif int(valor) in rango_bajo:
        luz_solar = "baja"
    else:
        luz_solar = "desconocida"
    return luz_solar

def leerSensorLM35():
    global temperatura
    temperatura = (sensor_temperatura.read_u16() * (3.3/65535.0)) * 100 - 8
    return temperatura

def leerSensorDHT11():
    global humedad
    while True:
        try:
            dht11Sensor.measure()
            humedad = dht11Sensor.humidity()
            break 
        except OSError:
            humedad = None
            time.sleep_ms(200)
    return humedad

def pagina_web():
  html = """<!DOCTYPE HTML><html>
<head>
  <meta http-equiv=\"refresh\" content=\"2\" charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
  <style>
    #panel-inferior {
      text-align: center;
      width: 40%;
      padding: 10px;
      margin: 0 auto;
      border-radius: 5px;
      background-color: #eaf7ff; /* Color de fondo */
    }
    .panel {
      background-color: #eaf7ff; /* Color de fondo */
      border-radius: 10px;
      margin-bottom: 10px;
      padding: 2px;
    }
  	body {
  	background-image: url('https://img.freepik.com/foto-gratis/nube-blanca-cielo-azul_74190-2381.jpg?w=2000');
  	background-repeat: no-repeat;
 	background-size: cover;
	}
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h2 { font-size: 2.0rem; }
    h3 { font-size: 2.0rem; }
    p { font-size: 2.0rem; }
    .units { font-size: 1.2rem; }
    .bme-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
  </style>
</head>

<body>
  <div class="panel" >
  	<div class="panel-header" style="margin-bottom: 0;">
  		<h2 style="margin-bottom: 0; color:#00204a">OVNITRIX</h2>
        <p class="bme-labels" style="margin-top: 0; color:#005792">Estacion del clima</p>
  	</div>
</div>
 
  <div class="panel" id="panel-inferior">
  <div class="panel-header">
      <h3 style = "color:#00204a">Bogotá</h3>
    </div>
  <div class="panel-body">
  <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="bme-labels" style = "color:#00204a;">Temperatura:</span> 
    <span style = "color:#005792;">"""+str(round(temperatura,2))+ "°"+"""</span>
  </p>
  <p>
    <i class="fas fa-tint" style="color:#00add6;"></i> 
    <span class="bme-labels" style = "color:#00204a;">Humedad:</span>
    <span style = "color:#005792;">"""+ str(humedad) +"%""""</span>
  </p>
  <p>
    <i class="fas fa-cloud-sun-rain" style="color:#ffe700;"></i>
    <span class="bme-labels" style = "color:#00204a;">iluminación:</span>
    <span style = "color:#005792; font-size:1.7rem;">"""+ luz_solar +"""</span>
  </p>
    </div>
  </div>
  
</body>
</html>"""
  return html

def graficaTemperatura(yp, tiempo, x, y, var = [0.0,30], vpts=[25, 16, 40], hpts = [25, 55, 112]):
    """
    by: Sergio Andres Castaño Giraldo
    """
    oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
    oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
    oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
    oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
    
    y[1] = int((yp-var[0])/(var[1]-var[0]) * (vpts[1]-hpts[1]) + hpts[1]) #Interpolation
    if tiempo < hpts[2] - hpts[0]:
        x[1] = x[0]+1
    else:
        x[1] = hpts[2]
    
    oled.line(x[0],y[0],x[1],y[1],1)
    oled.show()
    
    y[0] = y[1]
    x[0] = x[1]
    
    if tiempo > hpts[2] - hpts[0]:
        oled.fill_rect(vpts[0],vpts[1],2,vpts[2],0)
        oled.fill_rect(vpts[0]-25, vpts[1],vpts[0],vpts[2]+5,0)
        oled.scroll(-1,0)
        oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
        oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
        oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
        oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
    else:
        tiempo += 1
    return tiempo,x,y

#variables globales para el uso de la funcion para graficar
tiempo = 0
y = [55, 55]
x = [25, 25]

#Configuracion de la pantalla oled
sda = machine.Pin(16)
scl = machine.Pin(17)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

#puerto
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

#Primera pantalla logo de raspberry
buffer = bytearray(logo)
fb = framebuf.FrameBuffer(buffer,128,64,framebuf.MONO_HLSB)

oled.fill(0)
oled.blit(fb,0,0)
oled.show()
sleep(3)
oled.fill(0)

while True:  
  conexion, direccion = s.accept()
  request = conexion.recv(1024)
  leerSensorLM35()
  leerSensorDHT11()
  leerFotoResistencia()
  #grafica
  tiempo,x,y = graficaTemperatura(temperatura, tiempo, x, y)
  oled.fill_rect(0,0,120,15,0)
  oled.text("Temp: {:.2f}".format(temperatura), 0, 0, 1)
  oled.show()
  sleep(1)
  respuesta = pagina_web()
  conexion.send('HTTP/1.1 200 OK\n')
  conexion.send('Content-Type: text/html\n')
  conexion.send('Connection: close\n\n')
  conexion.sendall(respuesta)
  conexion.close()