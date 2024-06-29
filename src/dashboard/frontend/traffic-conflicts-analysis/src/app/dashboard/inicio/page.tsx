"use client";

import { useEffect, useRef, useState } from "react";
import { CircularProgressbar } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (selectedFile && videoRef.current) {
      videoRef.current.src = URL.createObjectURL(selectedFile);
      videoRef.current.load(); // This ensures the video is reloaded
      videoRef.current.onerror = () => {
        console.error('Error loading video:', selectedFile.name);
      };
    }
  }, [selectedFile]);

  const supportedExtensions = ["mp4", "mov", "avi", "mkv", "webm"];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files ? e.target.files[0] : null;

    if (file) {
      setSelectedFile(file);
      console.log("File uploaded:", file.name);
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
                />
                Choose file
              </label>
              <p className="mx-5 my-auto text-center text-2xl font-bold">
                {selectedFile ? selectedFile.name : "No File"}
              </p>
            </div>

            <button className="rounded-[1.7em] bg-azul px-12 py-3 text-2xl font-bold text-white">
              Procesar
            </button>
          </div>
          <div>
            {selectedFile && isExtensionSupported(selectedFile.name, supportedExtensions) ? (
              <video ref={videoRef} width="800" controls className="m-auto"/>
            ) : (
              <img alt="Image Placeholder" className="m-auto w-[800px]" src="/Preview.png"/>
            )
            }
          </div>
        </div>
      </div>
      <div className="box-border w-full md:w-[30%]">
        <div className="justify-b flex h-full flex-col items-center justify-around">
          <h2 className="text-3xl font-semibold">Resultado</h2>
          <CircularProgressbar className="h-40" value={60} text={`60%`} />
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
