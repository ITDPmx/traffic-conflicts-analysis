"use client";

import { api } from "~/trpc/react";
import { twMerge } from "tailwind-merge";
import Link from "next/link";

export const UserRow = ({ userId, callerUserId }: { userId: string, callerUserId: string }) => {
    const {data: userData} = api.user.getUserDataById.useQuery({ userId: userId });
    const utils = api.useUtils();
  
    const modifyUser = api.user.modifyUserRole.useMutation(
      {
        onSuccess: () => {
          utils.user.getUserDataById.invalidate({userId: userId}).catch(console.error);
          alert("Usuario modificado");
        },
        onError: (error) => {
          alert("Error al modificar usuario: " + error.message);
        }
      }
    );
  
    return (
      <tr className="border-b odd:bg-white even:bg-gray-50">
        <th
          scope="row"
          className="whitespace-nowrap px-6 py-4 font-medium text-gray-900 "
        >
          {userData?.registered.toDateString() ?? "Sin fecha"}
        </th>
        <td className="px-6 py-4">
          <label className="inline-flex cursor-pointer items-center">
            <input type="checkbox" checked={userData?.role === "ADMIN"} 
              onChange={() => {
                modifyUser.mutate({ userId: userData?.id ?? "", isAdmin: userData?.role !== "ADMIN" });
              }
            }
            className="peer sr-only text-verde bg-verde" disabled={userId === callerUserId} />
            <div className={twMerge("peer relative h-6 w-11 rounded-full bg-gray-400 after:absolute after:start-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-verde peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rtl:peer-checked:after:-translate-x-full ",
               userId === callerUserId ? "bg-gray-100" : "")}></div>
          </label>
        </td>
        <td className="px-6 py-4">{userData?.name}</td>
        <td className="px-6 py-4 underline text-center">
          <Link href={`/dashboard/historial?id=${userData?.id}`}>
            {userData?.videos.length}
          </Link>
        </td>
        <td className="px-6 py-4">
          {userData?.lastLogin.toDateString() ?? "Sin fecha"}
        </td>
      </tr>
    );
  };
  