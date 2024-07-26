"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { useState } from "react";
import { FiMenu } from "react-icons/fi";
import { TfiClose } from "react-icons/tfi";

import type { UserRole } from "~/server/auth";

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
  ];

  const filterMenuItems = menuItems.filter((item) => {
    if (item.role) {
      return role === item.role;
    }

    return true;
  });

  return (
    <nav className="fixed left-0 top-0 z-10 w-full bg-verde p-5">
      <div className="container mx-auto flex items-center justify-between">
        <div className="text-4xl font-bold text-white">ITDP</div>
        <div className="hidden space-x-16 pr-8 md:flex">
          {filterMenuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`px-5 text-2xl font-semibold text-white duration-200 hover:border-b-8 ${location === item.path ? "border-b-8" : ""}`}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden">
          <button onClick={handleToggle} className="text-white">
            {isOpen ? <TfiClose className="h-6 w-6" /> : <FiMenu />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="pt-4 md:hidden">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`my-2 block p-2 text-2xl text-white duration-200 hover:border-l-4 ${location === item.path ? "border-l-4" : ""}`}
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
