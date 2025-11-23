import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  FileText, 
  Workflow, 
  Gauge, 
  HeadphonesIcon,
  Users,
  Plug,
  Settings
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs) => twMerge(clsx(inputs));

const AdminLayout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/health', label: 'System Health', icon: Activity },
    { path: '/logs', label: 'Logs', icon: FileText },
    { path: '/workflows', label: 'Workflows', icon: Workflow },
    { path: '/performance', label: 'Performance', icon: Gauge },
    { path: '/support', label: 'Client Support', icon: HeadphonesIcon },
    { path: '/users', label: 'User Management', icon: Users },
    { path: '/integrations', label: 'Integrations', icon: Plug },
    { path: '/settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">Omnify Admin</h1>
          <p className="text-sm text-gray-400">Backoffice</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors",
                  isActive 
                    ? "bg-indigo-600 text-white" 
                    : "text-gray-300 hover:bg-gray-800"
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <div className="text-sm text-gray-400">Admin User</div>
          <div className="text-sm font-medium">admin@omnify.com</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default AdminLayout;

