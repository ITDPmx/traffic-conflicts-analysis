from flask import Flask, request, jsonify
from BEV.BEV import BEV
import requests
import numpy as np
from pathlib import Path


app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/birdsEyeView', methods=['POST'])
def get_homography_BEV():
    id_video = request.get_json()["id"]
    bucket = request.get_json()["bucket"]
    path = request.get_json()["path"]
    frame, new_path = BEV.getFrame(bucket, path, id_video)
    output_path = '/shared_data/bev_' + id_video + '.mp4'
    hmatrix_path = "/shared_data/homography_matrix.txt"
    dims_path = "/shared_data/target_dim.txt"
    if Path(hmatrix_path).exists() and Path(dims_path).exists():
        hmatrix = np.loadtxt(hmatrix_path)
        dims = tuple(np.loadtxt(dims_path, dtype=float).astype(int).tolist())
        BEV.save_bev_video(new_path, output_path, hmatrix,  dims)
    else:
        hmatrix, dims = BEV.get_homography(frame, path, id_video)
        BEV.save_bev_video(new_path, output_path, hmatrix, dims)
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
