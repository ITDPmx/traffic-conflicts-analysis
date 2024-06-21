"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React, { useState } from 'react';
import { FiMenu } from "react-icons/fi";
import { TfiClose } from "react-icons/tfi";

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = usePathname();
  
  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const menuItems = [
    { name: 'Inicio', path: '/dashboard/inicio' },
    { name: 'Historial', path: '/dashboard/historial' },
    { name: 'Usuarios', path: '/dashboard/usuarios'},

  ];
  return (
    <nav className="fixed top-0 left-0 w-full bg-verde p-5 z-10">
      <div className="container mx-auto flex justify-between items-center">
        <div className="text-white text-4xl font-bold">ITDP</div>
        <div className="hidden md:flex space-x-16 pr-8">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`text-2xl font-semibold text-white duration-200 hover:border-b-8 px-5 ${location === item.path ? 'border-b-8' : ''}`}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden">
          <button onClick={handleToggle} className="text-white">
            {isOpen ? <TfiClose className="h-6 w-6" />: <FiMenu />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="md:hidden pt-4">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`block text-white text-2xl duration-200 hover:border-l-4 p-2 my-2 ${location === item.path ? 'border-l-4' : ''}`}
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