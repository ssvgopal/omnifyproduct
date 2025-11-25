import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import api from '@/services/api';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    organizationName: '',
    acceptTerms: false
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = 'Invalid email address';
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.organizationName.trim()) {
      newErrors.organizationName = 'Organization name is required';
    }

    if (!formData.acceptTerms) {
      newErrors.acceptTerms = 'You must accept the Terms of Service and Privacy Policy';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');

    if (!validateForm()) return;

    setLoading(true);

    try {
      // Use the multi-tenancy register endpoint
      const response = await axios.post(
        `${BACKEND_URL}/api/auth/register`,
        {
          organization: {
            name: formData.organizationName,
            slug: formData.organizationName.toLowerCase().replace(/\s+/g, '-')
          },
          admin: {
            email: formData.email,
            password: formData.password,
            first_name: formData.firstName,
            last_name: formData.lastName
          }
        }
      );

      // Store token if provided
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user_id', response.data.admin_user?.id || '');
        localStorage.setItem('organization_id', response.data.organization?.id || '');
      }

      // Show success message
      alert('Signup successful! Please check your email to verify your account.');
      navigate('/login');

    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Signup failed. Please try again.';
      setSubmitError(errorMessage);
      console.error('Signup error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center">Create your Omnify account</CardTitle>
          <CardDescription className="text-center">
            Start your free beta trial today
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* First Name */}
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                type="text"
                value={formData.firstName}
                onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                className={errors.firstName ? 'border-red-500' : ''}
                disabled={loading}
              />
              {errors.firstName && (
                <p className="text-red-500 text-sm">{errors.firstName}</p>
              )}
            </div>

            {/* Last Name */}
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input
                id="lastName"
                type="text"
                value={formData.lastName}
                onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                disabled={loading}
              />
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className={errors.email ? 'border-red-500' : ''}
                disabled={loading}
              />
              {errors.email && (
                <p className="text-red-500 text-sm">{errors.email}</p>
              )}
            </div>

            {/* Organization Name */}
            <div className="space-y-2">
              <Label htmlFor="organizationName">Organization Name</Label>
              <Input
                id="organizationName"
                type="text"
                value={formData.organizationName}
                onChange={(e) => setFormData({...formData, organizationName: e.target.value})}
                className={errors.organizationName ? 'border-red-500' : ''}
                disabled={loading}
              />
              {errors.organizationName && (
                <p className="text-red-500 text-sm">{errors.organizationName}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                className={errors.password ? 'border-red-500' : ''}
                disabled={loading}
              />
              {errors.password && (
                <p className="text-red-500 text-sm">{errors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                className={errors.confirmPassword ? 'border-red-500' : ''}
                disabled={loading}
              />
              {errors.confirmPassword && (
                <p className="text-red-500 text-sm">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Terms Acceptance */}
            <div className="flex items-start space-x-2">
              <Checkbox
                id="acceptTerms"
                checked={formData.acceptTerms}
                onCheckedChange={(checked) => setFormData({...formData, acceptTerms: checked})}
                disabled={loading}
              />
              <Label htmlFor="acceptTerms" className="text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                I accept the{' '}
                <Link to="/legal/terms" target="_blank" className="text-blue-600 hover:underline">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link to="/legal/privacy" target="_blank" className="text-blue-600 hover:underline">
                  Privacy Policy
                </Link>
              </Label>
            </div>
            {errors.acceptTerms && (
              <p className="text-red-500 text-sm">{errors.acceptTerms}</p>
            )}

            {submitError && (
              <Alert variant="destructive">
                <AlertDescription>{submitError}</AlertDescription>
              </Alert>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>

            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:underline">
                Sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Signup;

