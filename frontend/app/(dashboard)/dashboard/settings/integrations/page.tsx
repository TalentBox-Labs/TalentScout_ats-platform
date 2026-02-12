/**
 * Integrations settings page
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api';
import {
  Mail,
  Calendar,
  Video,
  MessageSquare,
  Github,
  Linkedin,
  Cloud,
  CheckCircle,
  AlertCircle,
  ExternalLink
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  connected: boolean;
  configurable: boolean;
  config?: {
    apiKey?: string;
    webhookUrl?: string;
    clientId?: string;
    clientSecret?: string;
  };
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'sendgrid',
      name: 'SendGrid',
      description: 'Send transactional emails and automated responses',
      icon: <Mail className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { apiKey: '' },
    },
    {
      id: 'google-calendar',
      name: 'Google Calendar',
      description: 'Sync interviews and schedule meetings',
      icon: <Calendar className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { clientId: '', clientSecret: '' },
    },
    {
      id: 'zoom',
      name: 'Zoom',
      description: 'Schedule and join video interviews',
      icon: <Video className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { apiKey: '', clientSecret: '' },
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Send notifications to Slack channels',
      icon: <MessageSquare className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { webhookUrl: '' },
    },
    {
      id: 'github',
      name: 'GitHub',
      description: 'Import candidates from GitHub profiles',
      icon: <Github className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { apiKey: '' },
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      description: 'Import candidates from LinkedIn profiles',
      icon: <Linkedin className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { apiKey: '' },
    },
    {
      id: 'aws-s3',
      name: 'AWS S3',
      description: 'Store and serve resume files securely',
      icon: <Cloud className="h-6 w-6" />,
      connected: false,
      configurable: true,
      config: { apiKey: '', clientSecret: '' },
    },
  ]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const data = await apiClient.getIntegrations();
      // Update integrations with server data
      setIntegrations(prev => prev.map(integration => ({
        ...integration,
        connected: data[integration.id]?.connected || false,
        config: { ...integration.config, ...data[integration.id]?.config },
      })));
    } catch (error) {
      console.error('Failed to load integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectIntegration = async (integrationId: string) => {
    setSaving(integrationId);
    try {
      await apiClient.connectIntegration(integrationId);
      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, connected: true }
          : integration
      ));
    } catch (error) {
      console.error('Failed to connect integration:', error);
    } finally {
      setSaving(null);
    }
  };

  const disconnectIntegration = async (integrationId: string) => {
    setSaving(integrationId);
    try {
      await apiClient.disconnectIntegration(integrationId);
      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, connected: false }
          : integration
      ));
    } catch (error) {
      console.error('Failed to disconnect integration:', error);
    } finally {
      setSaving(null);
    }
  };

  const updateConfig = async (integrationId: string, config: any) => {
    setSaving(integrationId);
    try {
      await apiClient.updateIntegrationConfig(integrationId, config);
      setIntegrations(prev => prev.map(integration =>
        integration.id === integrationId
          ? { ...integration, config: { ...integration.config, ...config } }
          : integration
      ));
    } catch (error) {
      console.error('Failed to update integration config:', error);
    } finally {
      setSaving(null);
    }
  };

  if (loading) {
    return <div className="p-6">Loading integrations...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="text-gray-500">Connect third-party services to enhance your ATS</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <Card key={integration.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    {integration.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{integration.name}</CardTitle>
                    <div className="flex items-center space-x-2 mt-1">
                      {integration.connected ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Not Connected
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">{integration.description}</p>

              {integration.configurable && integration.config && (
                <div className="space-y-3">
                  {integration.config.apiKey !== undefined && (
                    <div className="space-y-1">
                      <Label htmlFor={`${integration.id}-api-key`} className="text-xs">
                        API Key
                      </Label>
                      <Input
                        id={`${integration.id}-api-key`}
                        type="password"
                        placeholder="Enter API key..."
                        value={integration.config.apiKey}
                        onChange={(e) => {
                          const newConfig = { ...integration.config, apiKey: e.target.value };
                          setIntegrations(prev => prev.map(int =>
                            int.id === integration.id ? { ...int, config: newConfig } : int
                          ));
                        }}
                      />
                    </div>
                  )}

                  {integration.config.webhookUrl !== undefined && (
                    <div className="space-y-1">
                      <Label htmlFor={`${integration.id}-webhook`} className="text-xs">
                        Webhook URL
                      </Label>
                      <Input
                        id={`${integration.id}-webhook`}
                        placeholder="https://your-app.com/webhook"
                        value={integration.config.webhookUrl}
                        onChange={(e) => {
                          const newConfig = { ...integration.config, webhookUrl: e.target.value };
                          setIntegrations(prev => prev.map(int =>
                            int.id === integration.id ? { ...int, config: newConfig } : int
                          ));
                        }}
                      />
                    </div>
                  )}

                  {integration.config.clientId !== undefined && (
                    <div className="space-y-1">
                      <Label htmlFor={`${integration.id}-client-id`} className="text-xs">
                        Client ID
                      </Label>
                      <Input
                        id={`${integration.id}-client-id`}
                        placeholder="Enter client ID..."
                        value={integration.config.clientId}
                        onChange={(e) => {
                          const newConfig = { ...integration.config, clientId: e.target.value };
                          setIntegrations(prev => prev.map(int =>
                            int.id === integration.id ? { ...int, config: newConfig } : int
                          ));
                        }}
                      />
                    </div>
                  )}

                  {integration.config.clientSecret !== undefined && (
                    <div className="space-y-1">
                      <Label htmlFor={`${integration.id}-client-secret`} className="text-xs">
                        Client Secret
                      </Label>
                      <Input
                        id={`${integration.id}-client-secret`}
                        type="password"
                        placeholder="Enter client secret..."
                        value={integration.config.clientSecret}
                        onChange={(e) => {
                          const newConfig = { ...integration.config, clientSecret: e.target.value };
                          setIntegrations(prev => prev.map(int =>
                            int.id === integration.id ? { ...int, config: newConfig } : int
                          ));
                        }}
                      />
                    </div>
                  )}
                </div>
              )}

              <div className="flex space-x-2">
                {integration.connected ? (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => disconnectIntegration(integration.id)}
                      disabled={saving === integration.id}
                      className="flex-1"
                    >
                      Disconnect
                    </Button>
                    {integration.configurable && (
                      <Button
                        size="sm"
                        onClick={() => updateConfig(integration.id, integration.config)}
                        disabled={saving === integration.id}
                      >
                        Save Config
                      </Button>
                    )}
                  </>
                ) : (
                  <Button
                    onClick={() => connectIntegration(integration.id)}
                    disabled={saving === integration.id}
                    className="w-full"
                  >
                    {saving === integration.id ? 'Connecting...' : 'Connect'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Integration Status Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Integration Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {integrations.filter(i => i.connected).length}
              </div>
              <div className="text-sm text-gray-500">Connected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">
                {integrations.filter(i => !i.connected).length}
              </div>
              <div className="text-sm text-gray-500">Available</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {integrations.filter(i => i.configurable).length}
              </div>
              <div className="text-sm text-gray-500">Configurable</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                100%
              </div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}