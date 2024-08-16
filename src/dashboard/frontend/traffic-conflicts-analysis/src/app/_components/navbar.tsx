"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { useState } from "react";
import { FiMenu } from "react-icons/fi";
import { TfiClose } from "react-icons/tfi";

import { signOut } from "next-auth/react";

export const Navbar = ({ role }: { role?: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = usePathname();

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const menuItems = [
    { name: "Inicio", path: "/dashboard/inicio" },
    { name: "Historial", path: "/dashboard/historial" },
    { name: "Usuarios", path: "/dashboard/usuarios", role: "ADMIN" },
    { name: "Cerrar Sesión", path: "", onclick:() => signOut()},
  ];

  const filterMenuItems = menuItems.filter((item) => {
    if (item.role) {
      return role === item.role;
    }

    return true;
  });

  return (
    <nav className="fixed left-0 top-0 z-10 w-full border-b-4 border-b-verde bg-white">
      <div className="container mx-auto flex items-center justify-between h-24">
        <div className="text-2xl lg:text-4xl font-bold  text-gray-600">Identificador de conflictos viales</div>
        <div className="hidden space-x-8 lg:space-x-16 pr-8 md:flex">
          {filterMenuItems.map((item) => (
            <Link
              key={item.name}
              href={item?.path ?? ""}
              className={`px-5 text-sm lg:text-2xl text-gray-500 border-verde duration-200 hover:border-b-8 ${location === item.path ? "border-b-8" : ""}`}
              onClick={item.onclick}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden">
          <button onClick={handleToggle} className="text-black">
            {isOpen ? <TfiClose size={24} /> : <FiMenu size={24} />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="pt-4 md:hidden">
          {filterMenuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`my-2 block p-2 text-2xl text-white duration-200 border-verde hover:border-l-4 ${location === item.path ? "border-l-4" : ""}`}
              onClick={() => setIsOpen(false)}
            >
              {item.name}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
};
