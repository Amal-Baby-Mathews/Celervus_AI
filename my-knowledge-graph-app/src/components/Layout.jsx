import React from 'react';
import { Outlet, Link, NavLink } from 'react-router-dom';
import { Home, Upload, Network,Database } from 'lucide-react';
import ChatWidget from './ChatWidget/ChatWidget'; // Import the new widget

const Layout = () => {
  const navLinkClass = ({ isActive }) =>
    `flex items-center px-3 py-1.5 sm:px-4 sm:py-2 md:px-5 md:py-2.5 rounded-md transition-colors duration-200 text-sm sm:text-base font-medium ${
      isActive
        ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 font-semibold'
        : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
    }`;

  return (
    <div className="flex flex-col min-h-screen bg-gray-900 dark:bg-gray-900 text-white dark:text-white">
      <nav className="bg-white dark:bg-gray-800 shadow-md sticky top-0 z-10 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="flex items-center justify-between h-16 sm:h-20">
            <div className="flex items-center">
              <Link to="/" className="text-xl sm:text-2xl md:text-3xl font-bold text-blue-600 dark:text-blue-400 flex items-center">
                <Network size={28} className="mr-2 text-pink-600 dark:text-pink-400" />
                Celervus
              </Link>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6">
              <NavLink to="/" className={navLinkClass}>
                <Home size={20} className="mr-1 sm:mr-2" /> Home
              </NavLink>
              <NavLink to="/upload" className={navLinkClass}>
                <Upload size={20} className="mr-1 sm:mr-2" /> Upload PDF
              </NavLink>
              <NavLink to="/topics" className={navLinkClass}>
                <Network size={20} className="mr-1 sm:mr-2" /> View Topics
              </NavLink>
                            {/* --- NEW LINK --- */}
                            <NavLink to="/json-data" className={navLinkClass}>
                <Database size={18} className="mr-1 sm:mr-1.5" /> {/* Added JSON Data icon */}
                JSON Data
              </NavLink>
              {/* --- END NEW LINK --- */}
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-10">
        <Outlet />
      </main>

      <footer className="bg-gray-800 dark:bg-gray-900 text-gray-300 dark:text-gray-400 text-center p-4 sm:p-6 mt-8">
        © {new Date().getFullYear()} Celervus. All rights reserved.
      </footer>
            {/* Celerbud Chat Widget - Rendered persistently */}
            <ChatWidget />
    </div>
  );
};

export default Layout;