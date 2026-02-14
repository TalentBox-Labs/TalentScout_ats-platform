/**
 * Dashboard sidebar navigation component
 */
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  GitBranch,
  Calendar,
  Mail,
  BarChart3,
  Settings,
  FileText,
  Sparkles,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, implemented: true },
  { name: 'Jobs', href: '/dashboard/jobs', icon: Briefcase, implemented: true },
  { name: 'Candidates', href: '/dashboard/candidates', icon: Users, implemented: true },
  { name: 'Pipeline', href: '/dashboard/pipeline', icon: GitBranch, implemented: false }, // TODO: Implement pipeline view
  { name: 'Interviews', href: '/dashboard/interviews', icon: Calendar, implemented: false }, // TODO: Implement interview scheduling
  { name: 'Communications', href: '/dashboard/communications', icon: Mail, implemented: false }, // TODO: Implement email communications
  { name: 'Reports', href: '/dashboard/reports', icon: FileText, implemented: false }, // TODO: Implement reporting system
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3, implemented: false }, // TODO: Implement analytics dashboard
  { name: 'Settings', href: '/dashboard/settings', icon: Settings, implemented: false }, // TODO: Implement settings page
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex w-64 flex-col bg-white border-r border-gray-200 shadow-lg">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            TalentScout
          </h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-6">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
          const Icon = item.icon;

          if (!item.implemented) {
            return (
              <div
                key={item.name}
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-gray-400 cursor-not-allowed opacity-50"
                title="Coming soon"
              >
                <Icon className="h-5 w-5" />
                <span className="font-semibold">{item.name}</span>
              </div>
            );
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 group
                ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 hover:text-blue-600'
                }
              `}
            >
              <Icon className={`h-5 w-5 transition-transform duration-200 ${isActive ? 'text-white' : 'group-hover:scale-110'}`} />
              <span className="font-semibold">{item.name}</span>
              {isActive && (
                <div className="ml-auto w-2 h-2 bg-white rounded-full animate-pulse"></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-200 p-4 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold shadow-lg">
            JD
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">John Doe</p>
            <p className="text-xs text-gray-600 truncate">Administrator</p>
          </div>
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" title="Online"></div>
        </div>
      </div>
    </div>
  );
}
