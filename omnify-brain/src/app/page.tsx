import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center px-6">
        <h1 className="text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
          Omnify Brain
        </h1>
        <p className="text-2xl text-gray-700 mb-8">
          AI-Powered Marketing Intelligence
        </p>
        <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
          Unified attribution, predictive analytics, and prescriptive actions for modern marketing teams.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium shadow-lg hover:shadow-xl"
          >
            Get Started
          </Link>
          <a
            href="http://localhost:3001"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-50 transition-colors text-lg font-medium shadow-lg hover:shadow-xl border-2 border-blue-600"
          >
            View Demo
          </a>
        </div>
        <div className="mt-16 text-sm text-gray-500">
          <p>Production SaaS • Real-time Data • AI-Powered Insights</p>
        </div>
      </div>
    </div>
  );
}
