'use client';

import { useState } from 'react';

interface CompanyInfoStepProps {
  data: {
    companyName: string;
    industry: string;
    revenueRange: string;
  };
  onNext: (data: any) => void;
}

export function CompanyInfoStep({ data, onNext }: CompanyInfoStepProps) {
  const [formData, setFormData] = useState(data);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.companyName || !formData.industry || !formData.revenueRange) {
      setError('Please fill in all fields');
      return;
    }

    onNext(formData);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Tell us about your company</h2>
      <p className="text-gray-600 mb-6">This helps us customize your experience</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
            Company Name *
          </label>
          <input
            id="companyName"
            type="text"
            value={formData.companyName}
            onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Acme Inc."
          />
        </div>

        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
            Industry *
          </label>
          <select
            id="industry"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select industry</option>
            <option value="beauty">Beauty & Skincare</option>
            <option value="wellness">Health & Wellness</option>
            <option value="supplements">Supplements & Nutraceuticals</option>
            <option value="pet">Pet Care</option>
            <option value="apparel">Apparel & Lifestyle</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label htmlFor="revenueRange" className="block text-sm font-medium text-gray-700 mb-2">
            Annual Revenue *
          </label>
          <select
            id="revenueRange"
            value={formData.revenueRange}
            onChange={(e) => setFormData({ ...formData, revenueRange: e.target.value })}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select revenue range</option>
            <option value="50-100">$50M - $100M</option>
            <option value="100-150">$100M - $150M</option>
            <option value="150-250">$150M - $250M</option>
            <option value="250-350">$250M - $350M</option>
            <option value="350+">$350M+</option>
          </select>
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Continue
        </button>
      </form>
    </div>
  );
}

