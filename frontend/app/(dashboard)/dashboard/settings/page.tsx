/**
 * Settings and automation configuration page
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api';
import { Save, Mail, MessageSquare, Calendar, Zap } from 'lucide-react';

interface AutomationSettings {
  autoScreening: boolean;
  autoEmailResponses: boolean;
  autoScheduleInterviews: boolean;
  emailTemplates: {
    welcome: string;
    rejection: string;
    interviewInvite: string;
  };
  slackIntegration: boolean;
  calendarIntegration: boolean;
  webhookUrl?: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<AutomationSettings>({
    autoScreening: false,
    autoEmailResponses: false,
    autoScheduleInterviews: false,
    emailTemplates: {
      welcome: '',
      rejection: '',
      interviewInvite: '',
    },
    slackIntegration: false,
    calendarIntegration: false,
    webhookUrl: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await apiClient.get('/api/v1/settings/automation');
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
      // Keep default settings
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await apiClient.put('/api/v1/settings/automation', settings);
      // Show success message
    } catch (error) {
      console.error('Failed to save settings:', error);
      // Show error message
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: keyof AutomationSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const updateEmailTemplate = (template: keyof AutomationSettings['emailTemplates'], value: string) => {
    setSettings(prev => ({
      ...prev,
      emailTemplates: { ...prev.emailTemplates, [template]: value }
    }));
  };

  if (loading) {
    return <div className="p-6">Loading settings...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500">Configure automation and integrations</p>
        </div>
        <Button onClick={saveSettings} disabled={saving}>
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      {/* Automation Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            Automation Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="auto-screening">Auto Screening</Label>
              <p className="text-sm text-gray-500">
                Automatically screen candidates using AI when they apply
              </p>
            </div>
            <Switch
              id="auto-screening"
              checked={settings.autoScreening}
              onCheckedChange={(checked) => updateSetting('autoScreening', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="auto-emails">Auto Email Responses</Label>
              <p className="text-sm text-gray-500">
                Send automated email responses to candidates
              </p>
            </div>
            <Switch
              id="auto-emails"
              checked={settings.autoEmailResponses}
              onCheckedChange={(checked) => updateSetting('autoEmailResponses', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="auto-schedule">Auto Schedule Interviews</Label>
              <p className="text-sm text-gray-500">
                Automatically suggest interview times based on availability
              </p>
            </div>
            <Switch
              id="auto-schedule"
              checked={settings.autoScheduleInterviews}
              onCheckedChange={(checked) => updateSetting('autoScheduleInterviews', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Email Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Mail className="h-5 w-5 mr-2" />
            Email Templates
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="welcome-template">Welcome Email Template</Label>
            <Textarea
              id="welcome-template"
              placeholder="Welcome message sent to new applicants..."
              value={settings.emailTemplates.welcome}
              onChange={(e) => updateEmailTemplate('welcome', e.target.value)}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="rejection-template">Rejection Email Template</Label>
            <Textarea
              id="rejection-template"
              placeholder="Rejection message sent to unsuccessful candidates..."
              value={settings.emailTemplates.rejection}
              onChange={(e) => updateEmailTemplate('rejection', e.target.value)}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="interview-template">Interview Invite Template</Label>
            <Textarea
              id="interview-template"
              placeholder="Interview invitation message..."
              value={settings.emailTemplates.interviewInvite}
              onChange={(e) => updateEmailTemplate('interviewInvite', e.target.value)}
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      {/* Integrations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            Integrations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="slack-integration">Slack Integration</Label>
              <p className="text-sm text-gray-500">
                Send notifications to Slack channels
              </p>
            </div>
            <Switch
              id="slack-integration"
              checked={settings.slackIntegration}
              onCheckedChange={(checked) => updateSetting('slackIntegration', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="calendar-integration">Calendar Integration</Label>
              <p className="text-sm text-gray-500">
                Sync interviews with Google Calendar
              </p>
            </div>
            <Switch
              id="calendar-integration"
              checked={settings.calendarIntegration}
              onCheckedChange={(checked) => updateSetting('calendarIntegration', checked)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="webhook-url">Webhook URL</Label>
            <Input
              id="webhook-url"
              placeholder="https://your-app.com/webhook"
              value={settings.webhookUrl}
              onChange={(e) => updateSetting('webhookUrl', e.target.value)}
            />
            <p className="text-sm text-gray-500">
              Receive real-time updates about applications and interviews
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Onboarding */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Onboarding
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Complete Setup</h4>
                <p className="text-sm text-gray-500">
                  Finish configuring your ATS platform
                </p>
              </div>
              <Badge variant="secondary">In Progress</Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">Connect email service</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">Set up job templates</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm">Configure integrations</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <span className="text-sm">Invite team members</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}