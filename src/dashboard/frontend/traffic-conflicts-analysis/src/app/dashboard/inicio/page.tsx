"use client";

import { useEffect, useRef, useState } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import { api } from "~/trpc/react";
import "react-circular-progressbar/dist/styles.css";
import BeatLoader from "react-spinners/BeatLoader";
import { twMerge } from "tailwind-merge";

import axios from "axios";
import Link from "next/link";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [duration, setDuration] = useState(-1);
  const [progress, setProgress] = useState(0);

  const { data: lastFile } = api.video.getLastVideo.useQuery();

  const { data: isInstanceStopped, isLoading } = api.aws.isInstanceStopped.useQuery();

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
    <div className="flex h-[90vh] flex-col justify-between">
      <div className="h-[2vh]">
        <p className="text-white">a</p>
      </div>
      <div className="flex flex-col md:flex-row">
        <div className="box-border w-full md:w-[70%]">
          <div className="flex flex-col gap-y-8">
            <div className="flex flex-row  justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full border-4  border-verde p-7 text-3xl font-bold text-gris">
                1
              </div>
              <div className="mx-5 mb-5 flex max-w-[50%] flex-col items-start gap-y-6 text-lg">
                <p>
                  Sube un video de una intersección vial para analizar e
                  identificar los conflictos viales entre peatones, ciclistas y
                  vehículos.
                </p>
                <p>
                  Consulta el{" "}
                  <span className="underline">manual de usuario</span> o
                  descarga un <span className="underline">video de prueba</span>
                  .
                </p>
              </div>
            </div>
            {selectedFile &&
              !isExtensionSupported(selectedFile.name, supportedExtensions) && (
                <p className="text-center text-red-500">
                  Atención: el archivo subido no es válido. Extensiones
                  soportadas: {supportedExtensions.join(", ")}
                </p>
              )}

            {!isLoading && !isInstanceStopped &&
                (<h3 className="text-center text-red-500 text-lg">
                  Atención: el servidor de análisis se encuentra ocupado. Regresa más tarde para subir tu video.
                </h3>
              )}

            <div className="flex flex-row flex-wrap justify-around gap-y-4">
              <div className="ml-4 flex flex-row rounded-md border-2 border-black">
                <label
                  className={twMerge(
                    "custom-file-upload border-r-2 border-black bg-gray-400  p-3 text-center text-2xl font-bold text-white",
                    isInstanceStopped ? "bg-verde" : "",
                  )}
                >
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileUpload}
                    accept="video/*"
                    disabled={isLoading || !isInstanceStopped}
                  />
                  Escoger archivo
                </label>
                <p className="mx-5 my-auto text-center text-2xl font-bold text-verde">
                  {selectedFile ? selectedFile.name : "No File"}
                </p>
              </div>

              <button
                disabled={isLoading || !isInstanceStopped}
                className={twMerge(
                  "rounded-lg bg-gray-400  px-12 py-3 text-2xl font-bold text-white",
                  isInstanceStopped ? "bg-verde" : "",
                )}
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
                <div className="mx-auto flex h-[350px] w-[60%] rounded-lg shadow-full-border">
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
          <div className="flex flex-row">
            <div className="flex h-16 w-16 items-center justify-center rounded-full border-4  border-verde p-7 text-3xl font-bold text-gris">
              2
            </div>
            <div className="mx-5 mb-5 flex flex-col items-start gap-y-6 text-lg">
              <p>
                Descarga los resultados y analízalos en una herramienta como
                Excel o Google Sheets.
              </p>
              <p>
                También puedes revisar tu historial de videos analizados en
                {"  "}
                <Link className="underline" href={"/dashboard/historial"}>
                  Historial
                </Link>
                .
              </p>
            </div>
          </div>
          <div className="justify-b mr-[10%] flex flex-col items-center justify-around gap-y-4 rounded-3xl py-12 shadow-full-border">
            <h2 className="text-3xl font-bold text-verde">Resultados</h2>
            {lastFile && (
              <h2 className="mb-8 text-lg font-bold">({lastFile.name})</h2>
            )}

            <CircularProgressbar
              className="mb-8 h-32 text-verde"
              styles={buildStyles({
                textColor: "#00A94F",
                backgroundColor: "#00A94F",
                pathColor: "#00A94F",
              })}
              value={lastFile?.progress ?? 0}
              text={`${lastFile?.progress ?? 0}%`}
            />
            <button
              disabled={!lastFile || lastFile?.progress !== 100}
              onClick={() => {
                window.location.href = "/dashboard/historial";
              }}
            className={twMerge("rounded-lg bg-gray-400 px-12 py-3 text-2xl font-bold text-white", lastFile?.progress === 100 ? "bg-verde" : "")}>
              Descargar
            </button>
          </div>
        </div>
      </div>

      <div className="ml-[5%] flex flex-row items-center">
        <p className="text-center text-gris">Una colaboración de:</p>
        <div className="ml-7 mt-4 flex flex-row flex-wrap items-center space-x-4">
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
