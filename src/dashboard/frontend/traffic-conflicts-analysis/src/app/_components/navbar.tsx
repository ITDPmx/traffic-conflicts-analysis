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
    { name: 'Home', path: '/' },
    { name: 'About', path: '/about' },
    { name: 'Contact', path: '/contact' },
  ];
  return (
    <nav className="fixed top-0 left-0 w-full bg-gray-800 p-4 z-10">
      <div className="container mx-auto flex justify-between items-center">
        <div className="text-white text-xl font-bold">MyWebsite</div>
        <div className="hidden md:flex space-x-8">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`text-white hover:text-yellow-400 ${location === item.path ? 'border-b-2 border-yellow-400' : ''}`}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden">
          <button onClick={handleToggle} className="text-white">
            {isOpen ? <FiMenu /> : <TfiClose className="h-6 w-6" />}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="md:hidden">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`block text-white hover:text-yellow-400 p-2 ${location === item.path ? 'border-b-2 border-yellow-400' : ''}`}
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