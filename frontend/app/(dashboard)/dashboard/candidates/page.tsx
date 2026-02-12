/**
 * Candidates list page
 */
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Plus, Search, Mail, MapPin } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadCandidates();
  }, []);

  const loadCandidates = async () => {
    try {
      const data = await apiClient.getCandidates();
      setCandidates(data);
    } catch (error) {
      console.error('Failed to load candidates:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCandidates = candidates.filter((candidate: any) =>
    `${candidate.first_name} ${candidate.last_name} ${candidate.email}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Candidates</h1>
          <p className="text-gray-500">Manage your talent pool</p>
        </div>
        <Link href="/dashboard/candidates/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Candidate
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          type="search"
          placeholder="Search candidates by name or email..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i} className="p-6 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-gray-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 bg-gray-200 rounded w-1/4" />
                  <div className="h-4 bg-gray-200 rounded w-1/3" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredCandidates.map((candidate: any) => (
            <Link key={candidate.id} href={`/dashboard/candidates/${candidate.id}`}>
              <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
                <div className="flex items-center gap-4">
                  {/* Avatar */}
                  <div className="h-12 w-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {candidate.first_name[0]}{candidate.last_name[0]}
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">
                      {candidate.first_name} {candidate.last_name}
                    </h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                      {candidate.current_position && (
                        <span>{candidate.current_position}</span>
                      )}
                      {candidate.email && (
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {candidate.email}
                        </span>
                      )}
                      {candidate.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {candidate.location}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
