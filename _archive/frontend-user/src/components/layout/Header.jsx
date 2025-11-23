import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@omnify/shared-ui';
import { useAuth } from '@/contexts/AuthContext';
import { User, LogOut, Settings } from 'lucide-react';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-gray-900">
              Omnify
            </Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">
                  Dashboard
                </Link>
                <Link to="/insights" className="text-gray-600 hover:text-gray-900">
                  Insights
                </Link>
                <Link to="/workflows" className="text-gray-600 hover:text-gray-900">
                  Workflows
                </Link>
              </>
            ) : (
              <>
                <Link to="/features" className="text-gray-600 hover:text-gray-900">
                  Features
                </Link>
                <Link to="/pricing" className="text-gray-600 hover:text-gray-900">
                  Pricing
                </Link>
                <Link to="/demo" className="text-gray-600 hover:text-gray-900">
                  Demo
                </Link>
              </>
            )}
          </nav>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile">
                  <Button variant="ghost" size="sm" className="flex items-center">
                    <User className="h-4 w-4 mr-2" />
                    {user?.email?.split('@')[0] || 'Profile'}
                  </Button>
                </Link>
                <Link to="/settings">
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </Link>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="outline">Sign In</Button>
                </Link>
                <Link to="/demo">
                  <Button>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

