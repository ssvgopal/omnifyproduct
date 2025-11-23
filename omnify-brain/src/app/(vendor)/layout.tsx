'use client';

import { SessionProvider } from 'next-auth/react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Building2, 
  Activity, 
  DollarSign, 
  Shield, 
  Gauge, 
  Settings,
  LogOut 
} from 'lucide-react';

function VendorLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  if (status === 'loading') {
    return <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">Loading...</div>;
  }

  if (!session || (session.user as any)?.role !== 'vendor') {
    router.push('/dashboard');
    return null;
  }

  const navigation = [
    { name: 'Clients', href: '/vendor/clients', icon: Building2 },
    { name: 'Monitoring', href: '/vendor/monitoring', icon: Activity },
    { name: 'Billing', href: '/vendor/billing', icon: DollarSign },
    { name: 'Security', href: '/vendor/security', icon: Shield },
    { name: 'Quotas', href: '/vendor/quotas', icon: Gauge },
    { name: 'Settings', href: '/vendor/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-slate-950 border-r border-slate-800">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-2xl font-bold">⚡ Vendor Panel</h1>
          <p className="text-slate-400 text-sm mt-1">Super Admin Console</p>
        </div>

        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg mb-1 transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="flex-1">
              <p className="text-sm font-medium">{session.user?.name}</p>
              <p className="text-xs text-amber-400 font-medium">VENDOR</p>
            </div>
            <button
              onClick={() => router.push('/api/auth/signout')}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
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

export default function VendorLayoutWrapper({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <VendorLayout>{children}</VendorLayout>
    </SessionProvider>
  );
}
