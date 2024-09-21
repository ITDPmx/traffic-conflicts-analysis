import Link from "next/link";
import { getServerAuthSession } from "~/server/auth";
import { api } from "~/trpc/server";

export default async function History({searchParams} : {
    searchParams?: { [key: string]: string | string[] | undefined };
}) {

  const session = await getServerAuthSession();
  const id = searchParams?.id as string;

  const videoIds = await api.video.getUserVideosIds({
    userId: id ?? session?.user.id,
  });

  return (
    <div className="mx-auto flex w-full items-center">
      <div className="relative mx-auto mt-10 overflow-x-auto shadow-md sm:rounded-lg">
        <table className="w-full text-left text-sm text-gray-500 rtl:text-right dark:text-gray-400">
          <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Fecha
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Video
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Duración
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
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
        {videoIds.length === 0 && session?.user.role !== "ADMIN" && id !== session?.user.id && (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            Necesitas ser admin para ver los videos de alguien más.
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
      <td className="px-6 py-4 underline"><Link href={`/api/aws/s3?asset=original_video&id=${data?.id}`}>{data?.name ?? "Sin Nombre"}</Link></td>
      <td className="px-6 py-4">{Number(data?.duration) ?? "-1"}</td>
      <td className="px-6 py-4">{(data?.progress ?? 0) < 100 ? "En proceso." : (
        <div className="underline">
          <p><Link target="_blank" href={`/api/aws/s3?asset=processed_video&id=${data?.id}`}>Video Procesado</Link></p>
          <p><Link target="_blank" href={`/api/aws/s3?asset=summary&id=${data?.id}`}>Resumen</Link></p>
          <p><Link target="_blank" href={`/api/aws/s3?asset=full_data&id=${data?.id}`}>Todos los datos</Link></p>
        </div>

      )}</td>
    </tr>
  );
};
