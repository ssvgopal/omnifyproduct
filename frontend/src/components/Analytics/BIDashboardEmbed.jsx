import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Loader2,
  RefreshCw,
  Maximize2,
  Minimize2,
  AlertCircle,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign
} from 'lucide-react';
import api from '@/services/api';

const BIDashboardEmbed = ({ dashboardId, organizationId, userId }) => {
  const [embedUrl, setEmbedUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const iframeRef = useRef(null);

  useEffect(() => {
    if (dashboardId && organizationId && userId) {
      loadEmbedUrl();
    }
  }, [dashboardId, organizationId, userId]);

  const loadEmbedUrl = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get('/api/metabase/embedding/url', {
        params: {
          dashboard_id: dashboardId,
          organization_id: organizationId,
          user_id: userId
        }
      });

      if (response.data && response.data.embed_url) {
        setEmbedUrl(response.data.embed_url);
      } else {
        setError('Failed to load dashboard embed URL');
      }
    } catch (err) {
      console.error('Error loading embed URL:', err);
      setError('Failed to load dashboard. Please check Metabase configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadEmbedUrl();
  };

  const handleFullscreen = () => {
    if (!isFullscreen) {
      if (iframeRef.current?.requestFullscreen) {
        iframeRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">Loading dashboard...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-12">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button onClick={handleRefresh} className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={isFullscreen ? 'fixed inset-0 z-50 m-0 rounded-none' : ''}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Business Intelligence Dashboard</CardTitle>
            <CardDescription>Interactive analytics and insights</CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={handleFullscreen}>
              {isFullscreen ? (
                <>
                  <Minimize2 className="h-4 w-4 mr-2" />
                  Exit Fullscreen
                </>
              ) : (
                <>
                  <Maximize2 className="h-4 w-4 mr-2" />
                  Fullscreen
                </>
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {embedUrl && (
          <iframe
            ref={iframeRef}
            src={embedUrl}
            className="w-full border-0"
            style={{
              height: isFullscreen ? 'calc(100vh - 120px)' : '800px',
              minHeight: '600px'
            }}
            title="BI Dashboard"
            allowFullScreen
          />
        )}
      </CardContent>
    </Card>
  );
};

export default BIDashboardEmbed;

