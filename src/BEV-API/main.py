from flask import Flask, request, jsonify
from BEV.BEV import BEV
import requests
import numpy as np
from pathlib import Path


app = Flask(__name__)


@app.route('/defaultHBEV', methods=['POST'])
def defaultHBEV():
    id_video = request.get_json()["id"]
    bucket = request.get_json()["bucket"]
    path = request.get_json()["path"]
    _, new_path = BEV.getFrame(bucket, path, id_video)
    output_path = '/shared_data/bev_' + id_video + '.mp4'
    frame_path = '/shared_data/bev_' + id_video + '.png'
    hmatrix_path = "/shared_data/default_homography_matrix.txt"
    dims_path = "/shared_data/default_target_dim.txt"
    hmatrix = np.loadtxt(hmatrix_path)
    dims = tuple(np.loadtxt(dims_path, dtype=float).astype(int).tolist())
    BEV.save_bev_video(new_path, output_path, frame_path,hmatrix,  dims)
    response = requests.post('http://ttc:8001/process_video', json={"id_video": id_video})
    return jsonify({"result": "Success"})

@app.route('/getHBEV', methods=['POST'])
def get_BEV():
    id_video = request.get_json()["id"]
    bucket = request.get_json()["bucket"]
    path = request.get_json()["path"]
    frame, new_path = BEV.getFrame(bucket, path, id_video)
    output_path = '/shared_data/bev_' + id_video + '.mp4'
    frame_path = '/shared_data/bev_' + id_video + '.png'
    hmatrix_path = "/shared_data/homography_matrix.txt"
    dims_path = "/shared_data/target_dim.txt"
    hmatrix, dims = BEV.get_homography(frame, path, id_video)
    BEV.save_bev_video(new_path, output_path, frame_path, hmatrix, dims)
    BEV.uploadFile(frame_path, 'bevs/bev_' + id_video + '.png')
    response = requests.post('http://ttc:8001/process_video', json={"id_video": id_video})
    return jsonify({"result": "Success"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
