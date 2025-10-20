import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  SkipForward,
  Trophy,
  Star,
  Sparkles,
  Target,
  Users,
  Building,
  Link,
  Palette,
  Rocket,
  Zap,
  Crown,
  Gift,
  Clock,
  Play,
  Pause
} from 'lucide-react';
import api from '@/services/api';

const MagicalOnboardingWizard = () => {
  const [currentStep, setCurrentStep] = useState('welcome');
  const [stepConfig, setStepConfig] = useState(null);
  const [stepData, setStepData] = useState({});
  const [progress, setProgress] = useState({ percentage: 0, estimated_time_remaining: 15 });
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDemo, setShowDemo] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    loadOnboardingStatus();
  }, []);

  const loadOnboardingStatus = async () => {
    try {
      const response = await api.get('/api/onboarding/status');
      if (response.data.success) {
        const status = response.data.data;
        setCurrentStep(status.current_step);
        setProgress({
          percentage: status.progress_percentage,
          estimated_time_remaining: status.estimated_time_remaining
        });
        setAchievements(status.achievements);
        
        // Load current step configuration
        await loadStepConfiguration(status.current_step);
      }
    } catch (error) {
      console.error('Error loading onboarding status:', error);
    }
  };

  const loadStepConfiguration = async (stepName) => {
    try {
      const response = await api.get(`/api/onboarding/step/${stepName}`);
      if (response.data.success) {
        setStepConfig(response.data.config);
      }
    } catch (error) {
      console.error('Error loading step configuration:', error);
    }
  };

  const completeStep = async (stepData) => {
    try {
      setLoading(true);
      setIsAnimating(true);
      
      const response = await api.post('/api/onboarding/step/complete', {
        step: currentStep,
        data: stepData
      });
      
      if (response.data.success) {
        const result = response.data.data;
        setCurrentStep(result.current_step);
        setStepConfig(result.step_config);
        setProgress(result.progress);
        setAchievements(result.progress.achievements);
        
        // Show achievement notifications
        if (result.achievements_unlocked && result.achievements_unlocked.length > 0) {
          showAchievementNotification(result.achievements_unlocked);
        }
        
        // Load next step configuration
        await loadStepConfiguration(result.current_step);
      }
    } catch (error) {
      console.error('Error completing step:', error);
    } finally {
      setLoading(false);
      setIsAnimating(false);
    }
  };

  const skipStep = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/onboarding/step/skip', {
        step: currentStep,
        reason: 'User skipped step'
      });
      
      if (response.data.success) {
        const result = response.data.data;
        setCurrentStep(result.current_step);
        setStepConfig(result.step_config);
        setProgress(result.progress);
        
        // Load next step configuration
        await loadStepConfiguration(result.current_step);
      }
    } catch (error) {
      console.error('Error skipping step:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeOnboarding = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/onboarding/complete');
      
      if (response.data.success) {
        // Show completion celebration
        showCompletionCelebration();
        
        // Redirect to dashboard after delay
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 3000);
      }
    } catch (error) {
      console.error('Error completing onboarding:', error);
    } finally {
      setLoading(false);
    }
  };

  const showAchievementNotification = (newAchievements) => {
    // Implementation for achievement notification
    console.log('New achievements unlocked:', newAchievements);
  };

  const showCompletionCelebration = () => {
    // Implementation for completion celebration
    console.log('Onboarding completed!');
  };

  const handleRoleSelection = (role) => {
    completeStep({ role });
  };

  const handleCompanyInfo = (formData) => {
    completeStep(formData);
  };

  const handlePlatformConnection = (platforms) => {
    completeStep({ connected_platforms: platforms });
  };

  const handleBrandSetup = (brandData) => {
    completeStep({ brand_assets: brandData });
  };

  const handleCampaignCreation = (campaignData) => {
    completeStep({ campaign_type: campaignData.type, campaign_data: campaignData });
  };

  const getStepIcon = (stepName) => {
    const icons = {
      welcome: '🎉',
      role_selection: '👤',
      company_info: '🏢',
      platform_connection: '🔗',
      brand_setup: '🎨',
      first_campaign: '🚀',
      success_demo: '✨',
      completion: '🎊'
    };
    return icons[stepName] || '🎯';
  };

  const getAchievementIcon = (achievement) => {
    const icons = {
      first_steps: '👶',
      role_master: '🎭',
      company_builder: '🏢',
      platform_connector: '🔗',
      brand_artist: '🎨',
      campaign_creator: '🚀',
      magic_witness: '✨',
      omnify_master: '👑'
    };
    return icons[achievement] || '🏆';
  };

  if (!stepConfig) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-gray-500">Loading onboarding...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getStepIcon(currentStep)}</div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">OmniFy Onboarding</h1>
                <p className="text-sm text-gray-600">Step {Object.keys(stepConfig).length} of 8</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Progress Bar */}
              <div className="w-48">
                <Progress value={progress.percentage} className="h-2" />
                <p className="text-xs text-gray-500 mt-1">{Math.round(progress.percentage)}% complete</p>
              </div>
              
              {/* Time Remaining */}
              <div className="text-sm text-gray-600">
                <Clock className="h-4 w-4 inline mr-1" />
                {progress.estimated_time_remaining} min left
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className={`transition-all duration-500 ${isAnimating ? 'transform scale-105' : ''}`}>
          {/* Step Header */}
          <Card className="p-8 mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
            <div className="text-center">
              <div className="text-4xl mb-4">{stepConfig.icon}</div>
              <h2 className="text-3xl font-bold mb-2">{stepConfig.title}</h2>
              <p className="text-xl opacity-90 mb-4">{stepConfig.subtitle}</p>
              <p className="text-lg opacity-80">{stepConfig.description}</p>
            </div>
          </Card>

          {/* Step Content */}
          <Card className="p-8">
            {currentStep === 'welcome' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {stepConfig.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
                
                <div className="text-center">
                  <Button 
                    onClick={() => completeStep({})}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3 text-lg"
                  >
                    Let's Get Started! <ArrowRight className="h-5 w-5 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {currentStep === 'role_selection' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {stepConfig.options.map((option, index) => (
                    <Card 
                      key={index} 
                      className="p-6 cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-blue-500"
                      onClick={() => handleRoleSelection(option.role.value)}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-3">{option.icon}</div>
                        <h3 className="text-lg font-bold mb-2">{option.title}</h3>
                        <p className="text-sm text-gray-600 mb-4">{option.description}</p>
                        <div className="space-y-2">
                          {option.features.map((feature, idx) => (
                            <div key={idx} className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                              {feature}
                            </div>
                          ))}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {currentStep === 'company_info' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {stepConfig.fields.map((field, index) => (
                    <div key={index} className="space-y-2">
                      <Label htmlFor={field.name}>{field.label}</Label>
                      {field.type === 'select' ? (
                        <Select onValueChange={(value) => setStepData({...stepData, [field.name]: value})}>
                          <SelectTrigger>
                            <SelectValue placeholder={field.placeholder || `Select ${field.label}`} />
                          </SelectTrigger>
                          <SelectContent>
                            {field.options.map((option, idx) => (
                              <SelectItem key={idx} value={option}>{option}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : field.type === 'textarea' ? (
                        <Textarea 
                          id={field.name}
                          placeholder={field.placeholder}
                          onChange={(e) => setStepData({...stepData, [field.name]: e.target.value})}
                        />
                      ) : (
                        <Input 
                          id={field.name}
                          type={field.type}
                          placeholder={field.placeholder}
                          required={field.required}
                          onChange={(e) => setStepData({...stepData, [field.name]: e.target.value})}
                        />
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-between">
                  <Button variant="outline" onClick={skipStep}>
                    <SkipForward className="h-4 w-4 mr-2" />
                    Skip for Now
                  </Button>
                  <Button 
                    onClick={() => handleCompanyInfo(stepData)}
                    disabled={!stepData.company_name || !stepData.industry || !stepData.company_size}
                  >
                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {currentStep === 'platform_connection' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {stepConfig.platforms.map((platform, index) => (
                    <Card 
                      key={index} 
                      className="p-6 cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-blue-500"
                      onClick={() => {
                        const currentPlatforms = stepData.connected_platforms || [];
                        const updatedPlatforms = currentPlatforms.includes(platform.name)
                          ? currentPlatforms.filter(p => p !== platform.name)
                          : [...currentPlatforms, platform.name];
                        setStepData({...stepData, connected_platforms: updatedPlatforms});
                      }}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-3">{platform.icon}</div>
                        <h3 className="text-lg font-bold mb-2">{platform.title}</h3>
                        <p className="text-sm text-gray-600 mb-4">{platform.description}</p>
                        <div className="space-y-2">
                          {platform.features.map((feature, idx) => (
                            <div key={idx} className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                              {feature}
                            </div>
                          ))}
                        </div>
                        {(stepData.connected_platforms || []).includes(platform.name) && (
                          <div className="mt-4">
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Connected
                            </Badge>
                          </div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
                
                <div className="flex justify-between">
                  <Button variant="outline" onClick={skipStep}>
                    <SkipForward className="h-4 w-4 mr-2" />
                    Skip for Now
                  </Button>
                  <Button 
                    onClick={() => handlePlatformConnection(stepData.connected_platforms || [])}
                    disabled={!stepData.connected_platforms || stepData.connected_platforms.length === 0}
                  >
                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {currentStep === 'brand_setup' && (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <p className="text-gray-600">Upload your brand assets to enable AI-powered creative generation</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {stepConfig.upload_types.map((uploadType, index) => (
                    <div key={index} className="space-y-3">
                      <Label>{uploadType.label}</Label>
                      <p className="text-sm text-gray-600">{uploadType.description}</p>
                      
                      {uploadType.type === 'color_picker' ? (
                        <div className="flex space-x-2">
                          {uploadType.default_colors.map((color, idx) => (
                            <div 
                              key={idx}
                              className="w-12 h-12 rounded-lg border-2 border-gray-300 cursor-pointer hover:border-blue-500"
                              style={{ backgroundColor: color }}
                              onClick={() => {
                                const currentColors = stepData.brand_colors || [];
                                const updatedColors = currentColors.includes(color)
                                  ? currentColors.filter(c => c !== color)
                                  : [...currentColors, color];
                                setStepData({...stepData, brand_colors: updatedColors});
                              }}
                            />
                          ))}
                        </div>
                      ) : uploadType.type === 'font_selector' ? (
                        <Select onValueChange={(value) => setStepData({...stepData, [uploadType.name]: value})}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select font" />
                          </SelectTrigger>
                          <SelectContent>
                            {uploadType.options.map((font, idx) => (
                              <SelectItem key={idx} value={font}>{font}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : uploadType.type === 'textarea' ? (
                        <Textarea 
                          placeholder={uploadType.placeholder}
                          onChange={(e) => setStepData({...stepData, [uploadType.name]: e.target.value})}
                        />
                      ) : (
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 cursor-pointer">
                          <div className="text-gray-500">
                            <Palette className="h-8 w-8 mx-auto mb-2" />
                            <p>Click to upload {uploadType.label}</p>
                            <p className="text-xs">Max size: {uploadType.max_size}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-between">
                  <Button variant="outline" onClick={skipStep}>
                    <SkipForward className="h-4 w-4 mr-2" />
                    Skip for Now
                  </Button>
                  <Button onClick={() => handleBrandSetup(stepData)}>
                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {currentStep === 'first_campaign' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stepConfig.campaign_types.map((campaignType, index) => (
                    <Card 
                      key={index} 
                      className="p-6 cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-blue-500"
                      onClick={() => handleCampaignCreation(campaignType)}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-3">{campaignType.icon}</div>
                        <h3 className="text-lg font-bold mb-2">{campaignType.title}</h3>
                        <p className="text-sm text-gray-600 mb-4">{campaignType.description}</p>
                        <div className="space-y-2 text-xs text-gray-500">
                          <p><strong>Objective:</strong> {campaignType.sample_data.objective}</p>
                          <p><strong>Audience:</strong> {campaignType.sample_data.target_audience}</p>
                          <p><strong>Budget:</strong> {campaignType.sample_data.budget}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {currentStep === 'success_demo' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <div className="text-6xl mb-4">✨</div>
                  <h3 className="text-2xl font-bold mb-4">Watch the Magic Happen!</h3>
                  <p className="text-gray-600">Your campaign is now being optimized by OmniFy's AI</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {stepConfig.demo_features.map((feature, index) => (
                    <Card key={index} className="p-6">
                      <div className="flex items-center space-x-4">
                        <div className="text-3xl">{feature.icon}</div>
                        <div>
                          <h4 className="text-lg font-bold">{feature.title}</h4>
                          <p className="text-sm text-gray-600">{feature.description}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
                
                <div className="text-center">
                  <Button 
                    onClick={() => completeStep({})}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-8 py-3 text-lg"
                  >
                    Amazing! Continue <ArrowRight className="h-5 w-5 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {currentStep === 'completion' && (
              <div className="space-y-6">
                <div className="text-center">
                  <div className="text-6xl mb-4">🎉</div>
                  <h3 className="text-3xl font-bold mb-4">Congratulations!</h3>
                  <p className="text-xl text-gray-600 mb-8">You're now ready to experience the future of marketing</p>
                </div>
                
                {/* Achievements */}
                {achievements.length > 0 && (
                  <div className="mb-8">
                    <h4 className="text-lg font-bold mb-4 text-center">Achievements Unlocked!</h4>
                    <div className="flex flex-wrap justify-center gap-3">
                      {achievements.map((achievement, index) => (
                        <Badge key={index} className="bg-yellow-100 text-yellow-800 px-4 py-2">
                          <Trophy className="h-4 w-4 mr-2" />
                          {achievement.replace('_', ' ').toUpperCase()}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Next Steps */}
                <div className="mb-8">
                  <h4 className="text-lg font-bold mb-4">What's Next?</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {stepConfig.next_steps.map((step, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="text-gray-700">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="text-center">
                  <Button 
                    onClick={completeOnboarding}
                    className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white px-8 py-3 text-lg"
                  >
                    Enter OmniFy Dashboard <Crown className="h-5 w-5 ml-2" />
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Processing...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MagicalOnboardingWizard;
