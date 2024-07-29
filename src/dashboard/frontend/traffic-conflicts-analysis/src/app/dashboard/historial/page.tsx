import Link from "next/link";
import { redirect } from "next/navigation";

import { CreatePost } from "~/app/_components/create-post";
import { getServerAuthSession } from "~/server/auth";
import { api } from "~/trpc/server";

export default async function History() {
  const videoIds = await api.video.getUserVideosIds();

  return (
    <div className="mx-auto flex w-full items-center">
      <div className="relative mx-auto mt-10 overflow-x-auto shadow-md sm:rounded-lg">
        <table className="w-full text-left text-sm text-gray-500 rtl:text-right dark:text-gray-400">
          <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-azul"
              >
                Fecha
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-azul"
              >
                Video
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-azul"
              >
                Duración
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-azul"
              >
                Resultados
              </th>
            </tr>
          </thead>
          <tbody>
            {videoIds.map((videoId) => (
              <HistoryRow key={videoId.id} videoId={videoId.id} />
            ))}
          </tbody>
        </table>
        {videoIds.length === 0 && (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            No hay videos
          </div>
        )}
      </div>
    </div>
  );
}

const HistoryRow = async ({ videoId }: { videoId: string }) => {
  const data = await api.video.getUserVideosById({ videoId });

  return (
    <tr className="border-b odd:bg-white even:bg-gray-50 dark:border-gray-700 odd:dark:bg-gray-900 even:dark:bg-gray-800">
      <th
        scope="row"
        className="whitespace-nowrap px-6 py-4 font-medium text-gray-900 dark:text-white"
      >
        {data?.createdAt.toDateString()}
      </th>
      <td className="px-6 py-4">{data?.name ?? "Sin Nombre"}</td>
      <td className="px-6 py-4">{Number(data?.duration) ?? "-1"}</td>
      <td className="px-6 py-4">{data?.resultLink ?? "En proceso"}</td>
    </tr>
  );
};
