"use client";

import { useEffect, useRef, useState } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
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
      videoRef.current.onloadedmetadata = () => {
        setDuration(videoRef?.current?.duration ?? -1);
      };
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
                Math.round((progressEvent.loaded / progressEvent.total) * 100),
              );
            }
          },
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
    <div className="flex flex-col">
      <div className="mt-[75pt] flex flex-col md:flex-row">
        <div className="box-border w-full  md:w-[70%]">
          <div className="flex flex-col gap-y-8">
            {selectedFile &&
              !isExtensionSupported(selectedFile.name, supportedExtensions) && (
                <p className="text-center text-red-500">
                  Atención: el archivo subido no es válido. Extensiones
                  soportadas: {supportedExtensions.join(", ")}
                </p>
              )}
            <div className="flex flex-row flex-wrap justify-around gap-y-4">
              <div className="ml-4 flex flex-row rounded-md border-2 border-gray-400">
                <label className="custom-file-upload bg-verde p-3 text-center text-2xl font-bold text-white">
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileUpload}
                    accept="video/*"
                  />
                  Escoger archivo
                </label>
                <p className="mx-5 my-auto text-center text-2xl font-bold text-verde">
                  {selectedFile ? selectedFile.name : "No File"}
                </p>
              </div>

              <button
                className="rounded-[1.7em] bg-verde px-12 py-3 text-2xl font-bold text-white"
                onClick={async () => {
                  if (
                    selectedFile &&
                    isExtensionSupported(selectedFile.name, supportedExtensions)
                  ) {
                    getSignedUrl.mutate({
                      name: selectedFile.name,
                      duration: duration,
                    });
                  }
                }}
              >
                Procesar
              </button>
            </div>
            {isUploading && (
              <div className="mx-auto flex flex-row flex-wrap items-center gap-x-4 gap-y-5">
                <BeatLoader color="#41a85d" />
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
                <div className="border-2 border-black rounded-lg w-[60%] h-[450px] mx-auto flex">
                  <img
                    alt="Image Placeholder"
                    className="m-auto w-[200px]"
                    src="/Play.png"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="box-border w-full md:w-[30%]">
          <div className="justify-b mr-[10%] flex h-full flex-col items-center justify-around rounded-3xl border-2 border-black">
            <h2 className="text-3xl font-bold text-gray-600">Resultados</h2>
            <CircularProgressbar
              className="h-40 text-verde"
              styles={buildStyles({
                textColor: "#41a85d",
                backgroundColor: "#41a85d",
                pathColor: "#41a85d",
              })}
              value={0}
              text={`0%`}
            />
            <button className="rounded-[1.7em] bg-verde px-12 py-3 text-2xl font-bold text-white">
              Descargar
            </button>
          </div>
        </div>
      </div>

      <div className="ml-auto mr-[5%] mt-10">
        <div className="mt-4 flex flex-row flex-wrap items-center space-x-4">
          <img
            src="/ITDP_logo_completo.png"
            alt="ITDP Logo"
            className="h-20 object-contain"
          />
          <img
            src="/TEC_logo_completo.png"
            alt="Tec Logo"
            className="h-12 object-contain"
          />
          <img
            src="/FIA_logo_completo.png"
            alt="FIA Foundation Logo"
            className="h-11  object-contain"
          />
        </div>
      </div>
    </div>
  );
}

const isExtensionSupported = (fileName: string, extensions: string[]) => {
  const ext = fileName.split(".").pop();
  return ext ? extensions.includes(ext) : false;
};
