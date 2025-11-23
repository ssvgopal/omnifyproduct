import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token;
    const path = req.nextUrl.pathname;

    // Vendor routes - requires vendor role
    if (path.startsWith('/vendor')) {
      if (token?.role !== 'vendor') {
        return NextResponse.redirect(new URL('/dashboard', req.url));
      }
    }

    // Admin routes - requires admin or vendor role
    if (path.startsWith('/admin')) {
      if (token?.role !== 'admin' && token?.role !== 'vendor') {
        return NextResponse.redirect(new URL('/dashboard', req.url));
      }
    }

    // User routes (dashboard, analytics) - all authenticated users
    if (path.startsWith('/dashboard') || path.startsWith('/analytics') || path.startsWith('/campaigns')) {
      if (!token) {
        return NextResponse.redirect(new URL('/login', req.url));
      }
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/analytics/:path*',
    '/campaigns/:path*',
    '/admin/:path*',
    '/vendor/:path*',
    '/api/brain/:path*',
    '/api/sync/:path*',
    '/api/admin/:path*',
    '/api/vendor/:path*',
  ],
};
