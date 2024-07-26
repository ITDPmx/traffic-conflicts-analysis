import Link from "next/link";
import { redirect } from "next/navigation";

import { CreatePost } from "~/app/_components/create-post";
import { getServerAuthSession } from "~/server/auth";
import { api } from "~/trpc/server";


export default async function Home() {
  

  return (
    <div className="flex items-center mx-auto w-full">
      <div className="relative overflow-x-auto shadow-md sm:rounded-lg mx-auto mt-10">
        <table className="w-full text-left text-sm text-gray-500 rtl:text-right dark:text-gray-400">
          <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="px-6 py-3 text-xl text-azul normal-case text-center">
                Fecha
              </th>
              <th scope="col" className="px-6 py-3 text-xl text-azul normal-case text-center">
                Video
              </th>
              <th scope="col" className="px-6 py-3 text-xl text-azul normal-case text-center">
                Tiempo
              </th>
              <th scope="col" className="px-6 py-3 text-xl text-azul normal-case text-center">
                Resultados
              </th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b odd:bg-white even:bg-gray-50 dark:border-gray-700 odd:dark:bg-gray-900 even:dark:bg-gray-800">
              <th
                scope="row"
                className="whitespace-nowrap px-6 py-4 font-medium text-gray-900 dark:text-white"
              >
                Apple MacBook Pro 17&quot;
              </th>
              <td className="px-6 py-4">Silver</td>
              <td className="px-6 py-4">Laptop</td>
              <td className="px-6 py-4">$2999</td>
            </tr>
            
          </tbody>
        </table>
      </div>
    </div>
  );
}
