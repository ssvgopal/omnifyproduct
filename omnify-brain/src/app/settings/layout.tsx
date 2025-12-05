'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Settings, Building2, Users, Link2, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

const settingsNav = [
  { href: '/settings/organization', label: 'Organization', icon: Building2 },
  { href: '/settings/integrations', label: 'Integrations', icon: Link2 },
  { href: '/settings/users', label: 'Team Members', icon: Users },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard-v3"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4" />
                <span className="text-sm">Back to Dashboard</span>
              </Link>
              <div className="h-6 w-px bg-gray-200" />
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-gray-600" />
                <h1 className="text-lg font-semibold">Settings</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <nav className="w-64 shrink-0">
            <ul className="space-y-1">
              {settingsNav.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-purple-50 text-purple-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      )}
                    >
                      <Icon className="h-5 w-5" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Main Content */}
          <main className="flex-1 min-w-0">{children}</main>
        </div>
      </div>
    </div>
  );
}
