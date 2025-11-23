'use client';

import { SessionProvider } from 'next-auth/react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Users, 
  Plug, 
  CreditCard, 
  Settings, 
  LayoutDashboard,
  LogOut 
} from 'lucide-react';

function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  if (status === 'loading') {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!session || (session.user as any)?.role !== 'admin' && (session.user as any)?.role !== 'vendor') {
    router.push('/dashboard');
    return null;
  }

  const navigation = [
    { name: 'Overview', href: '/admin', icon: LayoutDashboard },
    { name: 'Team', href: '/admin/team', icon: Users },
    { name: 'Integrations', href: '/admin/integrations', icon: Plug },
    { name: 'Billing', href: '/admin/billing', icon: CreditCard },
    { name: 'Settings', href: '/admin/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-purple-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-purple-900 text-white">
        <div className="p-6">
          <h1 className="text-2xl font-bold">🔧 Admin Panel</h1>
          <p className="text-purple-200 text-sm mt-1">Organization Management</p>
        </div>

        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-colors ${
                  isActive
                    ? 'bg-purple-800 text-white'
                    : 'text-purple-200 hover:bg-purple-800 hover:text-white'
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-purple-800">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="flex-1">
              <p className="text-sm font-medium">{session.user?.name}</p>
              <p className="text-xs text-purple-300">{(session.user as any)?.role}</p>
            </div>
            <button
              onClick={() => router.push('/api/auth/signout')}
              className="p-2 hover:bg-purple-800 rounded-lg transition-colors"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 p-8">
        {children}
      </main>
    </div>
  );
}

export default function AdminLayoutWrapper({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AdminLayout>{children}</AdminLayout>
    </SessionProvider>
  );
}
