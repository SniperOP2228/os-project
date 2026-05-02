from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from os_engine import OSEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global OS Engine
engine = OSEngine()

def broadcast_state():
    socketio.emit('state_update', engine.get_state())

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('state_update', engine.get_state())

@socketio.on('create_process')
def handle_create_process(data):
    name = data.get('name')
    memory_size = data.get('memory_size', 512)
    engine.create_process(name, memory_size)
    broadcast_state()

@socketio.on('terminate_process')
def handle_terminate_process(data):
    pid = data.get('pid')
    engine.terminate_process(pid)
    broadcast_state()

@socketio.on('simulate_buffer_overflow')
def handle_overflow(data):
    pid = data.get('pid')
    engine.simulate_buffer_overflow(pid)
    broadcast_state()

@socketio.on('simulate_unauthorized_access')
def handle_unauthorized(data):
    source_pid = data.get('source_pid')
    target_pid = data.get('target_pid')
    engine.simulate_unauthorized_access(source_pid, target_pid)
    broadcast_state()

@socketio.on('setup_shared_memory')
def handle_shared_memory(data):
    pid1 = data.get('pid1')
    pid2 = data.get('pid2')
    engine.setup_shared_memory(pid1, pid2)
    broadcast_state()

@socketio.on('reset_engine')
def handle_reset():
    global engine
    engine = OSEngine()
    broadcast_state()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
