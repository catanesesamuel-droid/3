#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Domótica Vulnerable</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                .ventana { border: 2px solid #333; padding: 15px; margin: 10px; border-radius: 5px; }
                .cerrada { background: #ffcccc; }
                .abierta { background: #ccffcc; }
                .danger { background: #ff0000; color: white; }
                button { margin: 5px; padding: 10px; }
            </style>
        </head>
        <body>
            <h1>🏠 Control Domótica Vulnerable</h1>
            
            <div class="ventana cerrada" id="sala">
                <h3>🪟 Ventana Sala</h3>
                <p>Estado: <span id="estado-sala">CERRADA</span></p>
                <button onclick="controlar('sala', 'OPEN')">Abrir</button>
                <button onclick="controlar('sala', 'CLOSE')">Cerrar</button>
                <button class="danger" onclick="controlar('sala', 'OPEN FORCE')">⚠️ Forzar Apertura</button>
            </div>
            
            <div class="ventana cerrada" id="cocina">
                <h3>🪟 Ventana Cocina</h3>
                <p>Estado: <span id="estado-cocina">CERRADA</span></p>
                <button onclick="controlar('cocina', 'OPEN')">Abrir</button>
                <button onclick="controlar('cocina', 'CLOSE')">Cerrar</button>
                <button onclick="controlar('cocina', 'OPEN; system(\"reboot\")')">💀 Comando Malicioso</button>
            </div>
            
            <h3>📡 Terminal Simulada:</h3>
            <div style="background: #000; color: #0f0; padding: 10px; height: 200px; overflow-y: scroll; font-family: monospace;" id="terminal">
                Sistema iniciado...<br>
                Esperando comandos...<br>
            </div>
            
            <script>
                const terminal = document.getElementById('terminal');
                
                function log(msg) {
                    terminal.innerHTML += new Date().toLocaleTimeString() + ': ' + msg + '<br>';
                    terminal.scrollTop = terminal.scrollHeight;
                }
                
                function controlar(ventana, comando) {
                    log('🔓 Enviando: ' + ventana + ' -> ' + comando);
                    
                    // Simular vulnerabilidad
                    if (comando.includes('FORCE')) {
                        log('🚨 ¡SOBRECARGA DE MOTOR DETECTADA!');
                        log('⚡ Corriente: 5.2A (PELIGROSO)');
                        log('🔥 Temperatura: 90°C');
                        document.getElementById(ventana).classList.add('danger');
                    }
                    
                    if (comando.includes('system')) {
                        log('💀 POSIBLE EJECUCIÓN DE CÓDIGO REMOTO');
                        log('🚨 Sistema comprometido');
                    }
                    
                    // Cambiar estado visual
                    if (comando.includes('OPEN')) {
                        document.getElementById('estado-' + ventana).textContent = 'ABIERTA';
                        document.getElementById(ventana).className = 'ventana abierta';
                    } else if (comando.includes('CLOSE')) {
                        document.getElementById('estado-' + ventana).textContent = 'CERRADA';
                        document.getElementById(ventana).className = 'ventana cerrada';
                    }
                }
                
                // Simular ataque automático
                setTimeout(() => {
                    log('⚠️ Simulación de ataque en 5 segundos...');
                }, 5000);
                
                setTimeout(() => {
                    controlar('sala', 'OPEN FORCE; DROP TABLE devices');
                }, 10000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"[HTTP] Comando recibido: {post_data}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

print("🌐 Servidor web iniciado en http://localhost:8081")
print("📡 Simulador domótica vulnerable listo")
print("="*60)
print("Vulnerabilidades incluidas:")
print("1. Comandos sin autenticación")
print("2. Sobrecarga de motores")
print("3. Inyección de código")
print("4. Control total desde web")
print("="*60)

server = HTTPServer(('0.0.0.0', 8081), Handler)
server.serve_forever()