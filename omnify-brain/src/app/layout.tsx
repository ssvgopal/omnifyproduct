import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { PersonaProvider } from '@/lib/persona-context';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Omnify Brain',
  description: 'AI Marketing Intelligence Layer',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <PersonaProvider>
          {children}
        </PersonaProvider>
      </body>
    </html>
  );
}
