import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  Shield, 
  Lock, 
  Eye, 
  EyeOff, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Key,
  Database,
  ClipboardList,
  Settings,
  Download,
  Upload,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Clock,
  Users,
  Globe,
  Server,
  Zap
} from 'lucide-react';
import api from '@/services/api';

const SecurityComplianceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [securityPolicies, setSecurityPolicies] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [passwordStrength, setPasswordStrength] = useState(null);
  const [encryptionStatus, setEncryptionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testPassword, setTestPassword] = useState('');
  const [testData, setTestData] = useState('');
  const [encryptedData, setEncryptedData] = useState('');
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [policiesData, logsData, complianceData, healthData] = await Promise.all([
        api.get('/api/security/policies'),
        api.get('/api/security/audit/logs?limit=50'),
        api.get(`/api/security/compliance/overview/${clientId}`),
        api.get('/api/security/health')
      ]);
      
      setSecurityPolicies(policiesData.data.policies || []);
      setAuditLogs(logsData.data.logs || []);
      setComplianceStatus(complianceData.data);
      setEncryptionStatus(healthData.data);
    } catch (err) {
      console.error("Failed to fetch security data:", err);
      setError("Failed to load security data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const validatePassword = async () => {
    if (!testPassword) return;
    
    try {
      const response = await api.post('/api/security/password/validate', {
        password: testPassword
      });
      setPasswordStrength(response.data);
    } catch (err) {
      console.error("Failed to validate password:", err);
    }
  };

  const encryptData = async () => {
    if (!testData) return;
    
    try {
      const response = await api.post('/api/security/encrypt', {
        data: testData
      });
      setEncryptedData(response.data.encrypted_data);
    } catch (err) {
      console.error("Failed to encrypt data:", err);
    }
  };

  const getComplianceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getComplianceBadge = (isCompliant) => {
    return isCompliant ? (
      <Badge className="bg-green-500 text-white">
        <CheckCircle className="mr-1 h-3 w-3" /> Compliant
      </Badge>
    ) : (
      <Badge className="bg-red-500 text-white">
        <XCircle className="mr-1 h-3 w-3" /> Non-Compliant
      </Badge>
    );
  };

  const getSecurityLevelColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getEventTypeIcon = (eventType) => {
    switch (eventType) {
      case 'login': return <Key className="h-4 w-4 text-blue-500" />;
      case 'logout': return <Key className="h-4 w-4 text-gray-500" />;
      case 'data_access': return <Eye className="h-4 w-4 text-green-500" />;
      case 'data_modification': return <Database className="h-4 w-4 text-orange-500" />;
      case 'security_event': return <Shield className="h-4 w-4 text-red-500" />;
      default: return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) return <div className="text-center p-8">Loading Security & Compliance...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-red-50 to-orange-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-red-800 flex items-center">
              <Shield className="mr-2 h-6 w-6 text-red-500" /> Security & Compliance Dashboard
            </CardTitle>
            <CardDescription className="text-gray-700">
              Enterprise-grade security, encryption, audit logging, and compliance management
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={fetchData} variant="outline" className="flex items-center text-red-600 border-red-300 hover:bg-red-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button className="flex items-center text-white bg-red-600 hover:bg-red-700">
              <Download className="mr-2 h-4 w-4" /> Export Report
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Compliance Overview */}
      {complianceStatus && (
        <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-red-800 flex items-center">
              <CheckCircle className="mr-2 h-5 w-5 text-green-500" /> Compliance Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {complianceStatus.overall_score.toFixed(1)}%
                </div>
                <div className="text-lg font-semibold text-gray-800">Overall Score</div>
                <div className="mt-2">
                  {getComplianceBadge(complianceStatus.overall_compliant)}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {complianceStatus.summary.total_requirements_met}
                </div>
                <div className="text-lg font-semibold text-gray-800">Requirements Met</div>
                <div className="text-sm text-gray-600">Across all frameworks</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-red-600 mb-2">
                  {complianceStatus.summary.total_violations}
                </div>
                <div className="text-lg font-semibold text-gray-800">Violations</div>
                <div className="text-sm text-gray-600">Requiring attention</div>
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-lg mb-3">GDPR Compliance</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>Score:</span>
                    <span className={`font-semibold ${getComplianceColor(complianceStatus.frameworks.gdpr.score)}`}>
                      {complianceStatus.frameworks.gdpr.score}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    {getComplianceBadge(complianceStatus.frameworks.gdpr.is_compliant)}
                  </div>
                  <Progress value={complianceStatus.frameworks.gdpr.score} className="h-2" />
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-3">SOC 2 Compliance</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>Score:</span>
                    <span className={`font-semibold ${getComplianceColor(complianceStatus.frameworks.soc2.score)}`}>
                      {complianceStatus.frameworks.soc2.score}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    {getComplianceBadge(complianceStatus.frameworks.soc2.is_compliant)}
                  </div>
                  <Progress value={complianceStatus.frameworks.soc2.score} className="h-2" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Security Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-red-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="policies" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Policies</TabsTrigger>
          <TabsTrigger value="encryption" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Encryption</TabsTrigger>
          <TabsTrigger value="audit" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Audit Logs</TabsTrigger>
          <TabsTrigger value="compliance" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Compliance</TabsTrigger>
          <TabsTrigger value="tools" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Security Tools</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Security Status */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                  <Shield className="mr-2 h-5 w-5 text-red-500" /> Security Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center">
                      <Lock className="h-5 w-5 text-green-500 mr-2" />
                      <span className="font-medium">Data Encryption</span>
                    </div>
                    <Badge className="bg-green-500 text-white">Active</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center">
                      <Key className="h-5 w-5 text-blue-500 mr-2" />
                      <span className="font-medium">Password Security</span>
                    </div>
                    <Badge className="bg-blue-500 text-white">Enforced</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-purple-500 mr-2" />
                      <span className="font-medium">Audit Logging</span>
                    </div>
                    <Badge className="bg-purple-500 text-white">Enabled</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center">
                      <ClipboardList className="h-5 w-5 text-orange-500 mr-2" />
                      <span className="font-medium">Security Policies</span>
                    </div>
                    <Badge className="bg-orange-500 text-white">{securityPolicies.length} Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Security Events */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-blue-500" /> Recent Security Events
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {auditLogs.slice(0, 10).map((log) => (
                      <div key={log.log_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getEventTypeIcon(log.event_type)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{log.action}</div>
                          <div className="text-xs text-gray-600">
                            {log.user_id} • {new Date(log.timestamp).toLocaleString()}
                          </div>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {log.event_type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Policies Tab */}
        <TabsContent value="policies">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800">Security Policies</CardTitle>
              <CardDescription>Manage security policies and compliance requirements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityPolicies.map((policy) => (
                  <Card key={policy.policy_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{policy.name}</h3>
                        <p className="text-gray-600">{policy.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getSecurityLevelColor(policy.severity)} text-white`}>
                          {policy.severity}
                        </Badge>
                        <Badge variant="outline">{policy.compliance_frameworks.length} frameworks</Badge>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>Rules: {policy.rules.length}</div>
                      <div>Frameworks: {policy.compliance_frameworks.join(', ')}</div>
                    </div>
                    <div className="mt-3">
                      <Button variant="outline" size="sm">
                        <Settings className="mr-2 h-3 w-3" /> Configure
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Encryption Tab */}
        <TabsContent value="encryption">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                <Lock className="mr-2 h-5 w-5 text-green-500" /> Data Encryption
              </CardTitle>
              <CardDescription>Encrypt and decrypt sensitive data</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-lg mb-4">Encrypt Data</h3>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="data-to-encrypt">Data to Encrypt</Label>
                      <Textarea
                        id="data-to-encrypt"
                        placeholder="Enter sensitive data to encrypt..."
                        value={testData}
                        onChange={(e) => setTestData(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <Button onClick={encryptData} disabled={!testData}>
                      <Lock className="mr-2 h-4 w-4" /> Encrypt Data
                    </Button>
                    {encryptedData && (
                      <div className="mt-4">
                        <Label>Encrypted Data</Label>
                        <Textarea
                          value={encryptedData}
                          readOnly
                          className="mt-1 font-mono text-sm"
                        />
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-lg mb-4">Encryption Status</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <Database className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">AES-256-GCM</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Active</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center">
                        <Shield className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-medium">PII Encryption</span>
                      </div>
                      <Badge className="bg-blue-500 text-white">Enabled</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center">
                        <Key className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="font-medium">Key Management</span>
                      </div>
                      <Badge className="bg-purple-500 text-white">Secure</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Logs Tab */}
        <TabsContent value="audit">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                <FileText className="mr-2 h-5 w-5 text-blue-500" /> Audit Logs
              </CardTitle>
              <CardDescription>Comprehensive audit trail for compliance</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-3">
                  {auditLogs.map((log) => (
                    <Card key={log.log_id} className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getEventTypeIcon(log.event_type)}
                          <span className="ml-2 font-semibold">{log.action}</span>
                        </div>
                        <Badge variant="outline">{log.event_type}</Badge>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>User: {log.user_id}</div>
                        <div>Resource: {log.resource}</div>
                        <div>IP: {log.ip_address}</div>
                        <div>Time: {new Date(log.timestamp).toLocaleString()}</div>
                      </div>
                      {log.details && Object.keys(log.details).length > 0 && (
                        <div className="mt-2 text-xs text-gray-500">
                          Details: {JSON.stringify(log.details)}
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                <CheckCircle className="mr-2 h-5 w-5 text-green-500" /> Compliance Management
              </CardTitle>
              <CardDescription>Monitor compliance with various frameworks</CardDescription>
            </CardHeader>
            <CardContent>
              {complianceStatus && (
                <div className="space-y-6">
                  {/* GDPR Compliance */}
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-lg">GDPR Compliance</h3>
                      {getComplianceBadge(complianceStatus.frameworks.gdpr.is_compliant)}
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Compliance Score:</span>
                        <span className={`font-semibold ${getComplianceColor(complianceStatus.frameworks.gdpr.score)}`}>
                          {complianceStatus.frameworks.gdpr.score}%
                        </span>
                      </div>
                      <Progress value={complianceStatus.frameworks.gdpr.score} className="h-2" />
                    </div>
                    {complianceStatus.frameworks.gdpr.violations.length > 0 && (
                      <div className="mt-3">
                        <h4 className="font-medium text-red-600">Violations:</h4>
                        <ul className="text-sm text-red-600 mt-1">
                          {complianceStatus.frameworks.gdpr.violations.map((violation, index) => (
                            <li key={index}>• {violation}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* SOC 2 Compliance */}
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-lg">SOC 2 Compliance</h3>
                      {getComplianceBadge(complianceStatus.frameworks.soc2.is_compliant)}
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Compliance Score:</span>
                        <span className={`font-semibold ${getComplianceColor(complianceStatus.frameworks.soc2.score)}`}>
                          {complianceStatus.frameworks.soc2.score}%
                        </span>
                      </div>
                      <Progress value={complianceStatus.frameworks.soc2.score} className="h-2" />
                    </div>
                    {complianceStatus.frameworks.soc2.violations.length > 0 && (
                      <div className="mt-3">
                        <h4 className="font-medium text-red-600">Violations:</h4>
                        <ul className="text-sm text-red-600 mt-1">
                          {complianceStatus.frameworks.soc2.violations.map((violation, index) => (
                            <li key={index}>• {violation}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tools Tab */}
        <TabsContent value="tools">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                <Zap className="mr-2 h-5 w-5 text-yellow-500" /> Security Tools
              </CardTitle>
              <CardDescription>Test and validate security measures</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Password Strength Tester */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">Password Strength Tester</h3>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="password-test">Test Password</Label>
                      <Input
                        id="password-test"
                        type="password"
                        placeholder="Enter password to test..."
                        value={testPassword}
                        onChange={(e) => setTestPassword(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <Button onClick={validatePassword} disabled={!testPassword}>
                      <Shield className="mr-2 h-4 w-4" /> Test Password
                    </Button>
                    {passwordStrength && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">Strength Score:</span>
                          <span className={`font-bold ${passwordStrength.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                            {passwordStrength.score}/5
                          </span>
                        </div>
                        <Progress value={(passwordStrength.score / 5) * 100} className="h-2 mb-3" />
                        {passwordStrength.errors.length > 0 && (
                          <div className="text-sm text-red-600">
                            <strong>Errors:</strong>
                            <ul className="mt-1">
                              {passwordStrength.errors.map((error, index) => (
                                <li key={index}>• {error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {passwordStrength.suggestions.length > 0 && (
                          <div className="text-sm text-blue-600 mt-2">
                            <strong>Suggestions:</strong>
                            <ul className="mt-1">
                              {passwordStrength.suggestions.map((suggestion, index) => (
                                <li key={index}>• {suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Security Health Check */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">Security Health Check</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Encryption Manager</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Healthy</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Password Manager</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Healthy</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Audit Logger</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Healthy</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Policy Manager</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Healthy</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Compliance Manager</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Healthy</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityComplianceDashboard;
