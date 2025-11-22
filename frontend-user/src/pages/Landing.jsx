import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '@omnify/shared-ui';
import { 
  BarChart3, 
  Zap, 
  Target, 
  TrendingUp,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

const Landing = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Stop Flying Blind. Start Making
              <span className="text-indigo-600"> Data-Driven Decisions</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Omnify unifies your marketing data across platforms, predicts what's coming, 
              and tells you exactly what to do next. No more guesswork. No more wasted spend.
            </p>
            <div className="flex justify-center space-x-4">
              <Link to="/demo">
                <Button size="lg" className="text-lg px-8">
                  Try Demo
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/pricing">
                <Button size="lg" variant="outline" className="text-lg px-8">
                  View Pricing
                </Button>
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-500">
              No credit card required • 14-day free trial
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Maximize ROAS
            </h2>
            <p className="text-xl text-gray-600">
              Three powerful modules working together
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="p-6">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <BarChart3 className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold ml-4">MEMORY</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Unified attribution across all platforms. See the truth behind your marketing performance.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Multi-touch attribution
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Cross-platform unified reporting
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Real-time data sync
                </li>
              </ul>
            </Card>

            <Card className="p-6">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Zap className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold ml-4">ORACLE</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Predictive intelligence that spots problems before they impact revenue.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  7-day creative fatigue prediction
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Early warning alerts
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Risk factor analysis
                </li>
              </ul>
            </Card>

            <Card className="p-6">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-green-100 rounded-lg">
                  <Target className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold ml-4">CURIOSITY</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Prescriptive recommendations that tell you exactly what to do next.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Actionable budget shift recommendations
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  Expected impact calculations
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  One-click execution
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">18%</div>
              <div className="text-gray-600">Reduction in wasted ad spend</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">$270k</div>
              <div className="text-gray-600">Saved annually (average)</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">3.5x</div>
              <div className="text-gray-600">Average ROAS improvement</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-indigo-600 mb-2">15min</div>
              <div className="text-gray-600">Weekly reporting time (vs 3 hours)</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Stop Wasting Budget?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join CMOs who've eliminated guesswork and maximized ROAS
          </p>
          <Link to="/demo">
            <Button size="lg" variant="secondary" className="text-lg px-8">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Landing;
