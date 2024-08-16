import { api } from "~/trpc/server";

import { getServerSession } from "next-auth";
import { UserRow } from "~/app/_components/UserRow";

export default async function Users() {
  const userIds= await api.user.getUserIds();

  const session = await getServerSession();

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
                Fecha de registro
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Admin
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Nombre
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Videos procesados
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xl normal-case text-verde"
              >
                Último ingreso
              </th>
            </tr>
          </thead>
          <tbody>
            {userIds?.map((userId) => (
              <UserRow key={userId.id} userId={userId.id} callerUserId={session?.user.id ?? ""} />
            ))}
          </tbody>
        </table>
        {userIds?.length === 0 && (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            No hay usuarios
          </div>
        )}
      </div>
    </div>
  );
}

