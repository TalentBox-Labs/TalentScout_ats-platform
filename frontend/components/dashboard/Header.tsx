/**
 * Dashboard header component
 */
'use client';

import { Bell, Search, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200/50 bg-white/80 backdrop-blur-sm px-8 shadow-sm">
      {/* Search */}
      <div className="flex-1 max-w-2xl">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <Input
            type="search"
            placeholder="Search candidates, jobs, or anything..."
            className="pl-12 h-11 rounded-xl border-gray-200/50 bg-gray-50/50 focus:bg-white transition-all duration-200 text-sm placeholder:text-gray-500 shadow-sm"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        {/* AI Assistant Button */}
        <Button
          variant="outline"
          size="sm"
          className="hidden sm:flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200/50 hover:from-blue-100 hover:to-indigo-100 text-blue-700 font-medium rounded-lg px-4 shadow-sm"
        >
          <Sparkles className="h-4 w-4" />
          AI Assistant
        </Button>

        <ThemeToggle />

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative h-10 w-10 rounded-xl hover:bg-gray-100/50 transition-colors">
          <Bell className="h-5 w-5 text-gray-600" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-gradient-to-r from-red-500 to-pink-500 animate-pulse shadow-sm"></span>
        </Button>

        {/* Quick Actions */}
        <div className="hidden md:flex items-center gap-2">
          <div className="text-xs text-gray-500 font-medium">Quick Actions:</div>
          <Button
            variant="ghost"
            size="sm"
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 font-medium rounded-lg px-3"
          >
            + New Job
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 font-medium rounded-lg px-3"
          >
            + Add Candidate
          </Button>
        </div>
      </div>
    </header>
  );
}
