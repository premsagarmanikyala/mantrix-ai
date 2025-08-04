import { useState, useEffect } from 'react';
import { Search, ExternalLink, Clock, BookOpen } from 'lucide-react';

interface ExternalRoadmapSource {
  id: string;
  name: string;
  description: string;
  base_url: string;
  is_active: boolean;
}

interface ExternalRoadmapStep {
  title: string;
  description: string;
  type: string;
  estimated_time: number;
}

interface ExternalRoadmap {
  id: string;
  title: string;
  description: string;
  source: string;
  source_url?: string;
  topics: string[];
  difficulty?: string;
  estimated_duration?: number;
  steps: ExternalRoadmapStep[];
}

interface SearchResponse {
  roadmaps: ExternalRoadmap[];
  query: string;
  sources_searched: string[];
  total_found: number;
  status: string;
}

export default function ExternalRoadmapSearch() {
  const [sources, setSources] = useState<ExternalRoadmapSource[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ExternalRoadmap[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available sources on component mount
  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await fetch('/api/v1/external-roadmaps/sources');
      if (response.ok) {
        const sourcesData = await response.json();
        setSources(sourcesData);
        setSelectedSources(sourcesData.map((s: ExternalRoadmapSource) => s.id));
      }
    } catch (err) {
      console.error('Failed to fetch sources:', err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        query: searchQuery,
        sources: selectedSources.join(','),
        limit: '10'
      });

      const response = await fetch(`/api/v1/external-roadmaps/search?${params}`);
      
      if (response.ok) {
        const data: SearchResponse = await response.json();
        setSearchResults(data.roadmaps);
      } else {
        setError('Failed to search external roadmaps');
      }
    } catch (err) {
      setError('Network error occurred while searching');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSourceToggle = (sourceId: string) => {
    setSelectedSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  const formatDuration = (minutes?: number) => {
    if (!minutes) return 'Duration not specified';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins > 0 ? `${mins}m` : ''}`;
    }
    return `${mins}m`;
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'text-green-600 bg-green-100';
      case 'intermediate': return 'text-yellow-600 bg-yellow-100';
      case 'advanced': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          External Roadmap Search
        </h1>
        <p className="text-gray-600 mb-6">
          Discover learning roadmaps from open sources like GitHub, Roadmap.sh, and FreeCodeCamp
        </p>

        {/* Source Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Select Sources</h3>
          <div className="flex flex-wrap gap-3">
            {sources.map(source => (
              <label key={source.id} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source.id)}
                  onChange={() => handleSourceToggle(source.id)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">{source.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Search Input */}
        <div className="flex gap-3 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for learning paths (e.g., javascript, python, web development)"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-800">
            Found {searchResults.length} Roadmaps
          </h2>
          
          {searchResults.map(roadmap => (
            <div key={roadmap.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-800">
                      {roadmap.title}
                    </h3>
                    {roadmap.source_url && (
                      <a
                        href={roadmap.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-4 mb-3">
                    <span className="text-sm font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      {roadmap.source}
                    </span>
                    {roadmap.difficulty && (
                      <span className={`text-sm font-medium px-2 py-1 rounded ${getDifficultyColor(roadmap.difficulty)}`}>
                        {roadmap.difficulty}
                      </span>
                    )}
                    <div className="flex items-center gap-1 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">{formatDuration(roadmap.estimated_duration)}</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-600">
                      <BookOpen className="w-4 h-4" />
                      <span className="text-sm">{roadmap.steps.length} steps</span>
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{roadmap.description}</p>
                  
                  {roadmap.topics.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {roadmap.topics.map(topic => (
                        <span
                          key={topic}
                          className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Steps Preview */}
              {roadmap.steps.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-3">Learning Steps:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {roadmap.steps.slice(0, 6).map((step, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                            {step.type}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatDuration(step.estimated_time)}
                          </span>
                        </div>
                        <h5 className="font-medium text-sm mb-1">{step.title}</h5>
                        <p className="text-xs text-gray-600">{step.description}</p>
                      </div>
                    ))}
                    {roadmap.steps.length > 6 && (
                      <div className="bg-gray-50 p-3 rounded-lg flex items-center justify-center">
                        <span className="text-sm text-gray-500">
                          +{roadmap.steps.length - 6} more steps
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {searchResults.length === 0 && searchQuery && !isLoading && (
        <div className="bg-gray-100 rounded-lg p-8 text-center">
          <p className="text-gray-600">
            No roadmaps found for "{searchQuery}". Try different keywords or select different sources.
          </p>
        </div>
      )}
    </div>
  );
}