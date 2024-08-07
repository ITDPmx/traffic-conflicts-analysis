"use client";

import { useEffect, useRef, useState } from "react";
import { CircularProgressbar } from "react-circular-progressbar";
import { api } from "~/trpc/react";
import "react-circular-progressbar/dist/styles.css";
import BeatLoader from "react-spinners/BeatLoader";

import axios from "axios";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [duration, setDuration] = useState(-1);
  const [progress, setProgress] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (selectedFile && videoRef.current) {
      videoRef.current.src = URL.createObjectURL(selectedFile);
      videoRef.current.load(); // This ensures the video is reloaded
      videoRef.current.onerror = () => {
        console.error("Error loading video:", selectedFile.name);
      };
      videoRef.current.onloadedmetadata = () =>{
        setDuration(videoRef?.current?.duration ?? -1);
      }
    }
  }, [selectedFile]);

  const getSignedUrl = api.video.getSignedUrl.useMutation({
    onSuccess: async (presignedUrl) => {
      setIsUploading(true);
      setProgress(0);
      try {
        await axios.put(presignedUrl, selectedFile, {
          headers: {
            "Content-Type": selectedFile?.type ?? "",
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              setProgress(
                Math.round((progressEvent.loaded / progressEvent.total) * 100)
              );
            }
          }
        });
        alert("El archivo se subió correctamente.");
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Hubo un error al subir el archivo.");
      }
     
      setIsUploading(false);
      setProgress(0);
    },
    onError: (error) => {
      alert("Error al conseguir URL:" + error.message);
    },
  });

  const supportedExtensions = ["mp4", "mov", "avi", "mkv", "webm"];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files ? e.target.files[0] : null;

    if (file) {
      setSelectedFile(file);
    }
  };

  return (
    <div className="flex flex-col md:flex-row">
      <div className="box-border w-full pt-10 md:w-[70%]">
        <div className="flex flex-col gap-y-8">
          {selectedFile &&
            !isExtensionSupported(selectedFile.name, supportedExtensions) && (
              <p className="text-center text-red-500">
                Atención: el archivo subido no es válido. Extensiones
                soportadas: {supportedExtensions.join(", ")}
              </p>
            )}
          <div className="flex flex-row flex-wrap justify-around gap-y-4">
            <div className="ml-4 flex flex-row rounded-md border border-black">
              <label className="custom-file-upload border-r-2 border-black bg-azul p-3 text-center text-2xl font-bold text-white">
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                  accept="video/*"
                />
                Choose file
              </label>
              <p className="mx-5 my-auto text-center text-2xl font-bold">
                {selectedFile ? selectedFile.name : "No File"}
              </p>
            </div>

            <button
              className="rounded-[1.7em] bg-azul px-12 py-3 text-2xl font-bold text-white"
              onClick={async () => {
                if (
                  selectedFile &&
                  isExtensionSupported(selectedFile.name, supportedExtensions)
                ) {
                  getSignedUrl.mutate({ name: selectedFile.name, duration: duration });
                }
              }}
            >
              Procesar
            </button>
          </div>
          {isUploading && (
            <div className="mx-auto flex flex-row flex-wrap items-center gap-x-4 gap-y-5">
              <BeatLoader color="#0033a0" />
              <p className="text-2xl font-bold">
                Subiendo archivo, por favor espera. {progress}%
              </p>
            </div>
          )}
          <div>
            {selectedFile &&
            isExtensionSupported(selectedFile.name, supportedExtensions) ? (
              <video ref={videoRef} width="800" controls className="m-auto" />
            ) : (
              <img
                alt="Image Placeholder"
                className="m-auto w-[800px]"
                src="/Preview.png"
              />
            )}
          </div>
        </div>
      </div>
      <div className="box-border w-full md:w-[30%]">
        <div className="justify-b flex h-full flex-col items-center justify-around">
          <h2 className="text-3xl font-semibold">Resultado</h2>
          <CircularProgressbar className="h-40" value={0} text={`0%`} />
          <button className="rounded-[1.7em] bg-azul px-12 py-3 text-2xl font-bold text-white">
            Descargar
          </button>
        </div>
      </div>
    </div>
  );
}

const isExtensionSupported = (fileName: string, extensions: string[]) => {
  const ext = fileName.split(".").pop();
  return ext ? extensions.includes(ext) : false;
};
