import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '@omnify/shared-ui';
import { CheckCircle2 } from 'lucide-react';

const Pricing = () => {
  const plans = [
    {
      name: 'Starter',
      price: '$499',
      period: '/month',
      description: 'Perfect for small teams getting started',
      features: [
        'Unified attribution (3 platforms)',
        'Basic predictive alerts',
        'Weekly recommendations',
        'Email support',
        'Up to $50k monthly ad spend'
      ],
      cta: 'Start Free Trial',
      popular: false
    },
    {
      name: 'Professional',
      price: '$799',
      period: '/month',
      description: 'For growing marketing teams',
      features: [
        'Unified attribution (unlimited platforms)',
        'Advanced predictive alerts',
        'Daily recommendations',
        'Priority support',
        'Up to $500k monthly ad spend',
        'Workflow traces',
        'Advanced analytics'
      ],
      cta: 'Start Free Trial',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large organizations',
      features: [
        'Everything in Professional',
        'Custom integrations',
        'Dedicated account manager',
        'SLA guarantee',
        'Unlimited ad spend',
        'Custom reporting',
        'On-premise deployment option'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600">
            Choose the plan that fits your needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <Card 
              key={plan.name} 
              className={`p-8 relative ${plan.popular ? 'ring-2 ring-indigo-600 scale-105' : ''}`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-4">{plan.description}</p>
                <div className="flex items-baseline justify-center">
                  <span className="text-5xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600 ml-2">{plan.period}</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">{feature}</span>
                  </li>
                ))}
              </ul>
              <Link to={plan.name === 'Enterprise' ? '/contact' : '/demo'} className="block">
                <Button 
                  className="w-full" 
                  variant={plan.popular ? 'default' : 'outline'}
                  size="lg"
                >
                  {plan.cta}
                </Button>
              </Link>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            All plans include 14-day free trial. No credit card required.
          </p>
          <p className="text-sm text-gray-500">
            Compare with Northbeam ($2,500-3,500/month) • Save 70%+ with Omnify
          </p>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
