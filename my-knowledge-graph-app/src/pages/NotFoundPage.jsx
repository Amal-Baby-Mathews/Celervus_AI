// src/pages/NotFoundPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

const NotFoundPage = () => {
  return (
    <div className="text-center py-16">
       <AlertTriangle size={64} className="mx-auto text-red-500 mb-4" />
      <h1 className="text-4xl font-bold text-red-600 mb-2">404 - Page Not Found</h1>
      <p className="text-lg text-text-muted mb-6">
        Sorry, the page you are looking for does not exist.
      </p>
      <Link to="/" className="btn-primary">
        Go Back Home
      </Link>
    </div>
  );
};

export default NotFoundPage;