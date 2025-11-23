import NextAuth, { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { supabaseAdmin } from '@/lib/db/supabase';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Fetch user from Supabase
          const { data: user, error } = await supabaseAdmin
            .from('users')
            .select(`
              *,
              organization:organizations(*)
            `)
            .eq('email', credentials.email)
            .single();

          if (error || !user) {
            console.error('[AUTH] User not found:', error);
            return null;
          }

          // In production, verify password hash here
          // For now, simple check (REPLACE WITH PROPER HASH VERIFICATION)
          if (credentials.password !== 'demo') {
            return null;
          }

          return {
            id: user.id,
            email: user.email,
            name: user.email.split('@')[0],
            organizationId: user.organization_id,
            role: user.role,
          };
        } catch (error) {
          console.error('[AUTH] Authorization error:', error);
          return null;
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.organizationId = (user as any).organizationId;
        token.role = (user as any).role;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).organizationId = token.organizationId;
        (session.user as any).role = token.role;
      }
      return session;
    }
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
