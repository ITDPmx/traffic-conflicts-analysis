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
    { name: "Cerrar Sesión", path: "", onclick: () => signOut() },
  ];

  const filterMenuItems = menuItems.filter((item) => {
    if (item.role) {
      return role === item.role;
    }

    return true;
  });

  return (
    <nav className="fixed left-0 top-0 z-10 w-full border-b-4 border-b-verde bg-white">
      <div className="pl-4 container mx-auto flex h-[10vh] items-center justify-between">
        <div className="md:text-xl font-bold text-verde  lg:text-2xl">
          Identificador de conflictos viales
        </div>
        <div className="hidden space-x-8 pr-8 md:flex lg:space-x-16">
          {filterMenuItems.map((item) => (
            <Link
              key={item.name}
              href={item?.path ?? ""}
              className={`rounded-b-sm border-verde px-5 text-sm text-gray-500 duration-200 hover:border-b-4 lg:text-xl ${location === item.path ? "border-b-4" : ""}`}
              onClick={item.onclick}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden pr-4">
          <button onClick={handleToggle} className="text-black">
            {isOpen ? <TfiClose size={24} /> : <FiMenu size={24} />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="pl-4 pt-4 md:hidden">
          {filterMenuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`my-2 block border-verde p-2 text-gray-500 duration-200 hover:border-l-4 text-sm ${location === item.path ? "border-l-4" : ""}`}
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
