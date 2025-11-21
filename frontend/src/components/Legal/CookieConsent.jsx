import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Link } from 'react-router-dom';

const CookieConsent = () => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      setShowBanner(true);
    }
  }, []);

  const acceptCookies = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    setShowBanner(false);
    
    // Record acceptance in backend (optional, for analytics)
    // You can call the legal API here if needed
  };

  const declineCookies = () => {
    localStorage.setItem('cookie_consent', 'declined');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4">
      <Card className="max-w-4xl mx-auto shadow-lg">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex-1">
              <p className="text-sm text-gray-700">
                We use cookies to improve your experience, analyze site usage, and assist in our marketing efforts.
                By continuing to use our site, you consent to our use of cookies.{' '}
                <Link to="/legal/cookie" className="text-blue-600 hover:underline">
                  Learn more
                </Link>
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={acceptCookies}
                size="sm"
              >
                Accept All
              </Button>
              <Button
                onClick={declineCookies}
                variant="outline"
                size="sm"
              >
                Decline
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CookieConsent;

