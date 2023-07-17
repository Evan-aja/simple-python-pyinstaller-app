import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

def execute_binary(binary_path, args):
    try:
        cmd = [binary_path] + args
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr
    except Exception as e:
        return None, str(e)

@app.route('/execute', methods=['POST'])
def execute_endpoint():
    data = request.get_json()
    binary_path = data.get('binary_path', "${env.BUILD_ID}/sources/dist/add2vals")
    args = data.get('args', [])

    stdout, stderr = execute_binary(binary_path, args)

    if stdout:
        return jsonify({'stdout': stdout.decode('utf-8')})
    elif stderr:
        return jsonify({'stderr': stderr.decode('utf-8')})
    else:
        return jsonify({'error': 'Failed to execute the binary.'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12345)
