'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Building2, Save, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface Organization {
  id: string;
  name: string;
  industry?: string;
  annual_spend?: string;
  website?: string;
  created_at: string;
}

export default function OrganizationSettingsPage() {
  const { data: session } = useSession();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [annualSpend, setAnnualSpend] = useState('');
  const [website, setWebsite] = useState('');

  useEffect(() => {
    fetchOrganization();
  }, []);

  async function fetchOrganization() {
    try {
      const response = await fetch('/api/organization');
      if (response.ok) {
        const data = await response.json();
        setOrganization(data.organization);
        setName(data.organization.name || '');
        setIndustry(data.organization.metadata?.industry || '');
        setAnnualSpend(data.organization.metadata?.annualSpend || '');
        setWebsite(data.organization.website || '');
      }
    } catch (err) {
      console.error('Failed to fetch organization:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch('/api/onboarding/company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          industry,
          annualSpend,
          website,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to update organization');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-6 border-b">
        <div className="flex items-center gap-3">
          <Building2 className="h-6 w-6 text-purple-600" />
          <div>
            <h2 className="text-lg font-semibold">Organization Settings</h2>
            <p className="text-sm text-gray-500">
              Manage your organization profile and preferences
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            Organization settings saved successfully!
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="name">Organization Name *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              placeholder="Acme Inc."
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              type="url"
              value={website}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setWebsite(e.target.value)}
              placeholder="https://example.com"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="industry">Industry</Label>
            <select
              id="industry"
              value={industry}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setIndustry(e.target.value)}
              className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
            >
              <option value="">Select industry...</option>
              <option value="beauty">Beauty & Skincare</option>
              <option value="supplements">Supplements & Wellness</option>
              <option value="fashion">Fashion & Apparel</option>
              <option value="home">Home & Living</option>
              <option value="food">Food & Beverage</option>
              <option value="tech">Technology</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="annualSpend">Annual Ad Spend</Label>
            <select
              id="annualSpend"
              value={annualSpend}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAnnualSpend(e.target.value)}
              className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
            >
              <option value="">Select range...</option>
              <option value="<500k">Less than $500K</option>
              <option value="500k-1m">$500K - $1M</option>
              <option value="1m-5m">$1M - $5M</option>
              <option value="5m-10m">$5M - $10M</option>
              <option value=">10m">More than $10M</option>
            </select>
          </div>
        </div>

        <div className="pt-4 border-t flex justify-end">
          <Button type="submit" disabled={saving}>
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
