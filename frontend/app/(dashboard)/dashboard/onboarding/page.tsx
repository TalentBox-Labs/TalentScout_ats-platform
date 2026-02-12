/**
 * Onboarding flow for new users and team setup
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api';
import { CheckCircle, Circle, Users, Mail, Settings, Briefcase } from 'lucide-react';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
}

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [companyInfo, setCompanyInfo] = useState({
    name: '',
    website: '',
    description: '',
  });
  const [steps, setSteps] = useState<OnboardingStep[]>([
    {
      id: 'company',
      title: 'Company Information',
      description: 'Set up your company profile',
      completed: false,
      required: true,
    },
    {
      id: 'email',
      title: 'Email Integration',
      description: 'Connect your email service',
      completed: false,
      required: true,
    },
    {
      id: 'jobs',
      title: 'Create First Job',
      description: 'Post your first job opening',
      completed: false,
      required: true,
    },
    {
      id: 'team',
      title: 'Invite Team Members',
      description: 'Add colleagues to your team',
      completed: false,
      required: false,
    },
    {
      id: 'settings',
      title: 'Configure Settings',
      description: 'Set up automation and preferences',
      completed: false,
      required: false,
    },
  ]);

  useEffect(() => {
    loadOnboardingStatus();
  }, []);

  const loadOnboardingStatus = async () => {
    try {
      const data = await apiClient.getOnboardingStatus();
      setSteps(data.steps);
      setCurrentStep(data.currentStep);
    } catch (error) {
      console.error('Failed to load onboarding status:', error);
    }
  };

  const completeStep = async (stepId: string) => {
    try {
      await apiClient.completeOnboardingStep(stepId);
      setSteps(prev => prev.map(step =>
        step.id === stepId ? { ...step, completed: true } : step
      ));
      setCurrentStep(prev => prev + 1);
    } catch (error) {
      console.error('Failed to complete step:', error);
    }
  };

  const saveCompanyInfo = async () => {
    try {
      await apiClient.updateCompany(companyInfo);
      completeStep('company');
    } catch (error) {
      console.error('Failed to save company info:', error);
    }
  };

  const completedSteps = steps.filter(step => step.completed).length;
  const progress = (completedSteps / steps.length) * 100;

  const renderStepContent = () => {
    const step = steps[currentStep];
    if (!step) return null;

    switch (step.id) {
      case 'company':
        return (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <p className="text-gray-500">Tell us about your company</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="company-name">Company Name</Label>
                <Input
                  id="company-name"
                  placeholder="Acme Corporation"
                  value={companyInfo.name}
                  onChange={(e) => setCompanyInfo(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company-website">Website</Label>
                <Input
                  id="company-website"
                  placeholder="https://acme.com"
                  value={companyInfo.website}
                  onChange={(e) => setCompanyInfo(prev => ({ ...prev, website: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company-description">Company Description</Label>
                <Textarea
                  id="company-description"
                  placeholder="Tell candidates about your company..."
                  value={companyInfo.description}
                  onChange={(e) => setCompanyInfo(prev => ({ ...prev, description: e.target.value }))}
                  rows={4}
                />
              </div>

              <Button
                onClick={saveCompanyInfo}
                disabled={!companyInfo.name.trim()}
                className="w-full"
              >
                Save & Continue
              </Button>
            </CardContent>
          </Card>
        );

      case 'email':
        return (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Email Integration</CardTitle>
              <p className="text-gray-500">Connect your email service to send automated responses</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8">
                <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">SendGrid Integration</h3>
                <p className="text-gray-500 mb-6">
                  Connect SendGrid to send automated emails to candidates
                </p>
                <Button onClick={() => completeStep('email')}>
                  Connect SendGrid
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 'jobs':
        return (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Create Your First Job</CardTitle>
              <p className="text-gray-500">Post a job opening to start receiving applications</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Job Postings</h3>
                <p className="text-gray-500 mb-6">
                  Create your first job posting to attract candidates
                </p>
                <Button onClick={() => completeStep('jobs')}>
                  Create Job Posting
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 'team':
        return (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Invite Team Members</CardTitle>
              <p className="text-gray-500">Add colleagues to collaborate on hiring</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Team Collaboration</h3>
                <p className="text-gray-500 mb-6">
                  Invite team members to review applications and conduct interviews
                </p>
                <Button onClick={() => completeStep('team')}>
                  Invite Team Members
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 'settings':
        return (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Configure Settings</CardTitle>
              <p className="text-gray-500">Set up automation and preferences</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8">
                <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Automation & Preferences</h3>
                <p className="text-gray-500 mb-6">
                  Configure email templates, automation rules, and integrations
                </p>
                <Button onClick={() => completeStep('settings')}>
                  Configure Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to TalentScout</h1>
          <p className="text-gray-500 mt-2">Let's get your ATS platform set up</p>
        </div>

        {/* Progress Bar */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium">Setup Progress</span>
              <span className="text-sm text-gray-500">{completedSteps}/{steps.length} completed</span>
            </div>
            <Progress value={progress} className="w-full" />
          </CardContent>
        </Card>

        {/* Steps Overview */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center space-x-3 p-4 rounded-lg border ${
                step.completed
                  ? 'bg-green-50 border-green-200'
                  : index === currentStep
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              {step.completed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <Circle className={`h-5 w-5 ${index === currentStep ? 'text-blue-600' : 'text-gray-400'}`} />
              )}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${step.completed ? 'text-green-900' : 'text-gray-900'}`}>
                  {step.title}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Current Step Content */}
        {renderStepContent()}

        {/* Skip Option for Optional Steps */}
        {steps[currentStep] && !steps[currentStep].required && (
          <div className="text-center mt-6">
            <Button
              variant="ghost"
              onClick={() => setCurrentStep(prev => prev + 1)}
            >
              Skip this step
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}