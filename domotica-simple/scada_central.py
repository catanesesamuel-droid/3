#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import paho.mqtt.client as mqtt
import threading
from datetime import datetime
import socket
import time

# Configuración
MQTT_BROKER = "mqtt"
MQTT_PORT = 1883
HTTP_PORT = 8081
API_PORT = 5000

class SistemaSCADA:
    def __init__(self):
        self.estado_sistema = {
            "online": True,
            "timestamp": datetime.now().isoformat(),
            "sensores": {},
            "actuadores": {},
            "alarma": {"estado": "desarmada", "sensores": {}}
        }
        
        # Inicializar cliente MQTT
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="scada_central")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # Conectar a MQTT
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.mqtt_client.loop_start()
        
        print("🖥️  Sistema SCADA Central inicializado")
        print(f"📡 Conectado a MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print(f"✅ Conectado a broker MQTT. Código: {rc}")
        
        # Suscribirse a todos los tópicos relevantes
        topics = [
            ("casa/sensor/#", 1),
            ("casa/actuador/#", 1),
            ("casa/alarma/#", 2),
            ("casa/estado/#", 1)
        ]
        
        for topic, qos in topics:
            client.subscribe(topic, qos=qos)
            print(f"📨 Suscrito a: {topic}")
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            print(f"📩 [{topic}] -> {payload}")
            
            # Actualizar estado según el tópico
            if "sensor/luz" in topic:
                self.procesar_sensor_luz(payload)
            elif "sensor/temperatura" in topic:
                self.procesar_sensor_temperatura(payload)
            elif "actuador/luces" in topic:
                self.procesar_actuador_luces(payload)
            elif "actuador/persianas" in topic:
                self.procesar_actuador_persianas(payload)
            elif "alarma" in topic:
                self.procesar_alarma(payload)
                
        except Exception as e:
            print(f"❌ Error procesando mensaje MQTT: {e}")
    
    def procesar_sensor_luz(self, datos):
        zona = datos.get('zona', 'desconocida')
        self.estado_sistema["sensores"][f"luz_{zona}"] = {
            **datos,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        print(f"💡 Luz {zona}: {datos.get('valor')} ({datos.get('estado')})")
    
    def procesar_sensor_temperatura(self, datos):
        zona = datos.get('zona', 'desconocida')
        self.estado_sistema["sensores"][f"temp_{zona}"] = {
            **datos,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        print(f"🌡️  Temp {zona}: {datos.get('valor')}°C")
    
    def procesar_actuador_luces(self, datos):
        luz = datos.get('luz', 'desconocida')
        self.estado_sistema["actuadores"][f"luces_{luz}"] = {
            **datos,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        estado = "ON" if datos.get('estado') == 'on' else "OFF"
        print(f"💡 Luz {luz}: {estado} ({datos.get('intensidad')}%)")
    
    def procesar_actuador_persianas(self, datos):
        self.estado_sistema["actuadores"]["persianas"] = {
            **datos,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        print(f"🪟 Persianas: {datos.get('posicion')}%")
    
    def procesar_alarma(self, datos):
        self.estado_sistema["alarma"] = datos
        if datos.get('alerta_activa'):
            print("🚨 ALARMA ACTIVADA!")
    
    def enviar_comando(self, comando):
        """Envía comandos a los actuadores"""
        tipo = comando.get('tipo')
        
        if tipo == 'luces':
            self.mqtt_client.publish(
                f"casa/actuador/luces/comandos",
                json.dumps(comando),
                qos=2
            )
            print(f"📤 Comando luces: {comando}")
            
        elif tipo == 'persianas':
            self.mqtt_client.publish(
                f"casa/actuador/persianas/comandos",
                json.dumps(comando),
                qos=2
            )
            print(f"📤 Comando persianas: {comando}")
            
        elif tipo == 'alarma':
            self.mqtt_client.publish(
                f"casa/alarma/comandos",
                json.dumps(comando),
                qos=2
            )
            print(f"📤 Comando alarma: {comando}")
        
        return {"status": "comando_enviado", "comando": comando}

class HTTPHandler(BaseHTTPRequestHandler):
    scada = SistemaSCADA()
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/estado':
            self.serve_api_estado()
        elif self.path == '/api/sensores':
            self.serve_api_sensores()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Generar HTML del dashboard
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🏠 Sistema SCADA Domótica</title>
            <style>
                body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: white; border-radius: 10px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .sensor {{ border-left: 5px solid #4CAF50; }}
                .actuador {{ border-left: 5px solid #2196F3; }}
                .alarma {{ border-left: 5px solid #f44336; }}
                .estado-on {{ color: #4CAF50; font-weight: bold; }}
                .estado-off {{ color: #f44336; }}
                .control-panel {{ background: #333; color: white; padding: 15px; border-radius: 5px; }}
                button {{ padding: 10px 15px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }}
                .btn-on {{ background: #4CAF50; color: white; }}
                .btn-off {{ background: #f44336; color: white; }}
                .btn-alarma {{ background: #FF9800; color: white; }}
                .log {{ background: #000; color: #0f0; padding: 10px; font-family: monospace; height: 200px; overflow-y: scroll; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 Sistema SCADA Domótica</h1>
                <p>Sistema Central de Control y Supervisión</p>
                
                <div class="grid">
                    <!-- Panel de Sensores -->
                    <div class="card sensor">
                        <h2>📊 Sensores</h2>
                        <div id="sensores">
                            <p>Cargando sensores...</p>
                        </div>
                    </div>
                    
                    <!-- Panel de Actuadores -->
                    <div class="card actuador">
                        <h2>🎛️ Actuadores</h2>
                        <div class="control-panel">
                            <h3>💡 Luces</h3>
                            <button class="btn-on" onclick="controlarLuces('salon_principal', 'on', 100)">Encender Salón</button>
                            <button class="btn-off" onclick="controlarLuces('salon_principal', 'off', 0)">Apagar Salón</button>
                            <br>
                            <input type="range" min="0" max="100" value="50" onchange="controlarLuces('salon_principal', 'on', this.value)">
                            <span id="intensidad">50%</span>
                            
                            <h3>🪟 Persianas</h3>
                            <button class="btn-on" onclick="controlarPersianas(100)">Subir 100%</button>
                            <button onclick="controlarPersianas(50)">50%</button>
                            <button class="btn-off" onclick="controlarPersianas(0)">Bajar 0%</button>
                        </div>
                    </div>
                    
                    <!-- Panel de Alarma -->
                    <div class="card alarma">
                        <h2>🚨 Sistema de Alarma</h2>
                        <div id="estado-alarma">
                            <p>Estado: <span class="estado-off">DESARMADA</span></p>
                        </div>
                        <button class="btn-alarma" onclick="controlarAlarma('armar')">🔒 Armar Alarma</button>
                        <button class="btn-off" onclick="controlarAlarma('desarmar')">🔓 Desarmar</button>
                        <button onclick="controlarAlarma('test')">✅ Test</button>
                    </div>
                </div>
                
                <!-- Log del sistema -->
                <div class="card">
                    <h2>📝 Log del Sistema</h2>
                    <div class="log" id="log">
                        Sistema SCADA iniciado...<br>
                        Esperando datos de sensores...<br>
                    </div>
                </div>
                
                <!-- Estado del sistema -->
                <div class="card">
                    <h2>🖥️ Estado del Sistema</h2>
                    <pre id="estado-sistema">Cargando...</pre>
                </div>
            </div>
            
            <script>
                const logDiv = document.getElementById('log');
                const estadoDiv = document.getElementById('estado-sistema');
                const sensoresDiv = document.getElementById('sensores');
                const alarmaDiv = document.getElementById('estado-alarma');
                
                function log(msg) {{
                    logDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + msg + '<br>';
                    logDiv.scrollTop = logDiv.scrollHeight;
                }}
                
                function controlarLuces(luz, estado, intensidad) {{
                    const comando = {{
                        tipo: 'luces',
                        accion: estado === 'on' ? 'encender' : 'apagar',
                        luz: luz,
                        intensidad: parseInt(intensidad)
                    }};
                    
                    fetch('/api/comando', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(comando)
                    }}).then(r => r.json()).then(data => {{
                        log('💡 Comando luces enviado: ' + JSON.stringify(data));
                    }});
                    
                    if (estado === 'on') {{
                        document.getElementById('intensidad').textContent = intensidad + '%';
                    }}
                }}
                
                function controlarPersianas(posicion) {{
                    const comando = {{
                        tipo: 'persianas',
                        accion: posicion === 0 ? 'bajar' : 'subir',
                        porcentaje: posicion
                    }};
                    
                    fetch('/api/comando', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(comando)
                    }}).then(r => r.json()).then(data => {{
                        log('🪟 Comando persianas enviado: ' + JSON.stringify(data));
                    }});
                }}
                
                function controlarAlarma(accion) {{
                    const comando = {{
                        tipo: 'alarma',
                        accion: accion
                    }};
                    
                    fetch('/api/comando', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(comando)
                    }}).then(r => r.json()).then(data => {{
                        log('🚨 Comando alarma: ' + accion);
                        if (accion === 'armar') {{
                            alarmaDiv.innerHTML = '<p>Estado: <span class="estado-on">ARMADA</span></p>';
                        }} else if (accion === 'desarmar') {{
                            alarmaDiv.innerHTML = '<p>Estado: <span class="estado-off">DESARMADA</span></p>';
                        }}
                    }});
                }}
                
                // Actualizar estado periódicamente
                function actualizarEstado() {{
                    fetch('/api/estado')
                        .then(r => r.json())
                        .then(data => {{
                            estadoDiv.textContent = JSON.stringify(data, null, 2);
                        }});
                    
                    fetch('/api/sensores')
                        .then(r => r.json())
                        .then(sensores => {{
                            let html = '';
                            for (const [key, sensor] of Object.entries(sensores)) {{
                                html += `<p><strong>${{key}}</strong>: ${{sensor.valor}} ${{sensor.unidad || ''}}</p>`;
                            }}
                            sensoresDiv.innerHTML = html || '<p>No hay datos de sensores</p>';
                        }});
                }}
                
                // Simulación de datos en tiempo real
                setInterval(actualizarEstado, 2000);
                actualizarEstado();
                
                log('✅ Dashboard SCADA cargado');
                log('📡 Conectado al broker MQTT');
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def serve_api_estado(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Actualizar timestamp
        self.scada.estado_sistema["timestamp"] = datetime.now().isoformat()
        self.scada.estado_sistema["online"] = True
        
        response = {
            "status": "online",
            "sistema": self.scada.estado_sistema,
            "servicios": ["mqtt", "sensores", "actuadores", "alarma"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def serve_api_sensores(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = self.scada.estado_sistema["sensores"]
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        if self.path == '/api/comando':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                comando = json.loads(post_data.decode())
                resultado = self.scada.enviar_comando(comando)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resultado).encode())
                
                print(f"📨 Comando HTTP recibido: {comando}")
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)

def main():
    print("="*60)
    print("🏠 SISTEMA SCADA DOMÓTICA")
    print("="*60)
    print(f"🌐 Dashboard: http://localhost:{HTTP_PORT}")
    print(f"📡 API REST: http://localhost:{API_PORT}")
    print(f"🔌 MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🔌 MQTT WebSocket: ws://localhost:8080")
    print("="*60)
    
    # Iniciar servidor HTTP
    server = HTTPServer(('0.0.0.0', HTTP_PORT), HTTPHandler)
    
    # Iniciar servidor API en otro hilo
    def start_api_server():
        from flask import Flask, jsonify, request
        app = Flask(__name__)
        
        scada = HTTPHandler.scada
        
        @app.route('/api/status')
        def status():
            return jsonify({
                "status": "online",
                "service": "scada_api",
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route('/api/comando', methods=['POST'])
        def comando():
            data = request.json
            resultado = scada.enviar_comando(data)
            return jsonify(resultado)
        
        @app.route('/api/sensores')
        def sensores():
            return jsonify(scada.estado_sistema["sensores"])
        
        print(f"🚀 API REST iniciada en http://0.0.0.0:{API_PORT}")
        app.run(host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False)
    
    # Iniciar API en hilo separado
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("✅ Sistema SCADA completamente inicializado")
    print("🔄 Esperando conexiones...")
    
    server.serve_forever()

if __name__ == "__main__":
    main()