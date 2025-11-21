import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setStatus('error');
      setErrorMessage('Verification token is missing from the URL.');
      return;
    }

    // Call verification endpoint
    axios.get(`${BACKEND_URL}/api/auth/verify-email`, {
      params: { token }
    })
      .then((response) => {
        setStatus('success');
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      })
      .catch((error) => {
        setStatus('error');
        const errorMsg = error.response?.data?.detail || error.message || 'Email verification failed.';
        setErrorMessage(errorMsg);
      });
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Email Verification</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {status === 'verifying' && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
              <p className="text-gray-600">Verifying your email address...</p>
            </div>
          )}

          {status === 'success' && (
            <Alert>
              <AlertDescription>
                <div className="text-center space-y-4">
                  <p className="text-green-600 font-semibold">✅ Email verified successfully!</p>
                  <p className="text-gray-600">Redirecting to login page...</p>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {status === 'error' && (
            <div className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  <p className="font-semibold">Verification Failed</p>
                  <p className="mt-2">{errorMessage}</p>
                </AlertDescription>
              </Alert>
              <div className="flex gap-2">
                <Button
                  onClick={() => navigate('/login')}
                  className="flex-1"
                >
                  Go to Login
                </Button>
                <Button
                  onClick={() => navigate('/signup')}
                  variant="outline"
                  className="flex-1"
                >
                  Sign Up Again
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VerifyEmail;

