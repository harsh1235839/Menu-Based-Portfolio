from flask import Flask, request, jsonify, send_from_directory
import subprocess
import random

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'docker.html')

@app.route('/docker_image_pull', methods=['POST'])
def docker_img_pull():
    image = request.json.get('image')
    cmd = f"docker pull {image}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Image downloaded successfully.", "status": "success"})
    else:
        return jsonify({"message": "Image download failed.", "status": "fail"})

@app.route('/launch_docker', methods=['POST'])
def docker_launch():
    container_name = request.json.get('container_name')
    image = request.json.get('image')
    cmd = f"docker run -dit --name {container_name} {image}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Docker container launched successfully.", "status": "success", "container_id": output[1]})
    else:
        return jsonify({"message": "Failed to launch Docker container.", "status": "fail"})

@app.route('/docker_stop', methods=['POST'])
def docker_stop():
    container_name = request.json.get('container_name')
    cmd = f"docker stop {container_name}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Docker container stopped successfully.", "status": "success"})
    else:
        return jsonify({"message": "Failed to stop Docker container.", "status": "fail"})

@app.route('/docker_start', methods=['POST'])
def docker_start():
    container_name = request.json.get('container_name')
    cmd = f"docker start {container_name}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Docker container started successfully.", "status": "success"})
    else:
        return jsonify({"message": "Failed to start Docker container.", "status": "fail"})

@app.route('/docker_status', methods=['POST'])
def docker_status():
    container_name = request.json.get('container_name')
    cmd = f"docker ps -a --filter name={container_name} --format '{{{{.ID}}}} {{{{.Names}}}} {{{{.Status}}}}'"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": output[1], "status": "success"})
    else:
        return jsonify({"message": "Failed to get Docker container status.", "status": "fail"})

@app.route('/docker_remove', methods=['POST'])
def docker_remove():
    container_name = request.json.get('container_name')
    cmd = f"docker rm {container_name}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Docker container removed successfully.", "status": "success"})
    else:
        return jsonify({"message": "Failed to remove Docker container.", "status": "fail"})

@app.route('/docker_logs', methods=['POST'])
def docker_logs():
    container_name = request.json.get('container_name')
    cmd = f"docker logs {container_name}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": output[1], "status": "success"})
    else:
        return jsonify({"message": "Failed to get Docker container logs.", "status": "fail"})

@app.route('/docker_image_remove', methods=['POST'])
def docker_img_remove():
    image = request.json.get('image')
    cmd = f"docker rmi -f {image}"
    output = subprocess.getstatusoutput(cmd)
    if output[0] == 0:
        return jsonify({"message": "Docker image removed successfully.", "status": "success"})
    else:
        return jsonify({"message": "Failed to remove Docker image.", "status": "fail"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2000)
