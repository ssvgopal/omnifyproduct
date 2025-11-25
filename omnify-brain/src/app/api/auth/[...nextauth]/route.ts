import NextAuth, { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import { supabaseAdmin, supabase } from '@/lib/db/supabase';

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    }),
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
          // Use Supabase Auth to verify credentials
          const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
            email: credentials.email,
            password: credentials.password,
          });

          if (authError || !authData.user) {
            console.error('[AUTH] Authentication failed:', authError);
            // Surface a clearer error message to the client for common cases
            const code = (authError as any)?.code;
            if (code === 'email_not_confirmed') {
              throw new Error('Email not confirmed. Please check your inbox for the confirmation link.');
            }
            throw new Error('Invalid email or password.');
          }

          // Fetch user from our users table
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

          return {
            id: user.id,
            email: user.email,
            name: user.email.split('@')[0],
            organizationId: user.organization_id,
            role: user.role,
            authId: authData.user.id,
          };
        } catch (error) {
          console.error('[AUTH] Authorization error:', error);
          return null;
        }
      }
    })
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Handle Google OAuth sign-in
      if (account?.provider === 'google') {
        try {
          // Check if user exists in our database
          const { data: existingUser } = await supabaseAdmin
            .from('users')
            .select('*')
            .eq('email', user.email)
            .single();

          if (!existingUser) {
            // Create organization and user on first Google sign-in
            // This will be handled in the signup flow
            return true; // Allow sign-in, will create user in signup callback
          }
          return true;
        } catch (error) {
          console.error('[AUTH] Google sign-in error:', error);
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        token.organizationId = (user as any).organizationId;
        token.role = (user as any).role;
        token.authId = (user as any).authId;
      }
      
      // Handle Google OAuth - fetch user data
      if (account?.provider === 'google' && user?.email) {
        const { data: dbUser } = await supabaseAdmin
          .from('users')
          .select('*, organization:organizations(*)')
          .eq('email', user.email)
          .single();
        
        if (dbUser) {
          token.id = dbUser.id;
          token.organizationId = dbUser.organization_id;
          token.role = dbUser.role;
        }
      }
      
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id;
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
