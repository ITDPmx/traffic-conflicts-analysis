from flask import Flask, request, jsonify
from BEV.BEV import BEV
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/birdsEyeView', methods=['POST'])
def get_homography_BEV():
    id_video = request.get_json()["id"]
    bucket = request.get_json()["bucket"]
    path = request.get_json()["path"]

    frame = BEV.getFrame(bucket, path, id_video)
    BEV.get_homography(frame, path, id_video)

    response = requests.post('http://ttc:8001/process_video', json={"id_video": id_video})
    return jsonify({"result": "Success"})


@app.route('/getMatrix', methods=['POST'])
def get_matrix():
    bucket = request.get_json()["bucket"]
    path = request.get_json()["path"]
    BEV.getMatrix(bucket, path)
    print("Matrix generated")
    
    return jsonify({"result": "Success"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
