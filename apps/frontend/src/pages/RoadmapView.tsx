import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { 
  CheckCircle, 
  Clock, 
  Play, 
  Calendar,
  BookOpen,
  Award
} from 'lucide-react';

interface Module {
  id: string;
  title: string;
  duration: number;
  isCore: boolean;
  videoUrl?: string;
}

interface Branch {
  id: string;
  title: string;
  description: string;
  estimatedDuration: number;
  videos: Module[];
}

interface Roadmap {
  id: string;
  title: string;
  description: string;
  estimatedDuration: number;
  branches: Branch[];
}

interface Progress {
  moduleId: string;
  completed: boolean;
  completedAt?: string;
}

export default function RoadmapView() {
  const [searchParams] = useSearchParams();
  const roadmapId = searchParams.get('id');
  
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [progress, setProgress] = useState<Progress[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState<Module | null>(null);

  useEffect(() => {
    if (roadmapId) {
      fetchRoadmapAndProgress();
    }
  }, [roadmapId]);

  const fetchRoadmapAndProgress = async () => {
    try {
      setLoading(true);
      
      // Fetch roadmap details
      const roadmapResponse = await axios.get(`/api/v1/roadmap/id/${roadmapId}`);
      setRoadmap(roadmapResponse.data);
      
      // Fetch progress
      const progressResponse = await axios.get(`/api/v1/progress/summary?roadmap_id=${roadmapId}`);
      setProgress(progressResponse.data.completed_modules || []);
      
    } catch (error) {
      console.error('Error fetching roadmap data:', error);
    } finally {
      setLoading(false);
    }
  };

  const markModuleComplete = async (moduleId: string, branchId: string) => {
    try {
      await axios.post('/api/v1/progress/complete', {
        module_id: moduleId,
        branch_id: branchId,
        roadmap_id: roadmapId,
        duration_completed: 600 // Default 10 minutes
      });
      
      // Refresh progress
      await fetchRoadmapAndProgress();
    } catch (error) {
      console.error('Error marking module complete:', error);
    }
  };

  const isModuleCompleted = (moduleId: string) => {
    return progress.some(p => p.moduleId === moduleId && p.completed);
  };

  const calculateBranchProgress = (branch: Branch) => {
    const completedModules = branch.videos.filter(video => 
      isModuleCompleted(video.id)
    ).length;
    return Math.round((completedModules / branch.videos.length) * 100);
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Roadmap not found
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          The requested roadmap could not be loaded.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Roadmap Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {roadmap.title}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {roadmap.description}
            </p>
            <div className="flex items-center space-x-4 mt-4">
              <div className="flex items-center text-gray-500">
                <Clock className="h-4 w-4 mr-1" />
                <span>{formatDuration(roadmap.estimatedDuration)}</span>
              </div>
              <div className="flex items-center text-gray-500">
                <BookOpen className="h-4 w-4 mr-1" />
                <span>{roadmap.branches.length} branches</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round((progress.length / roadmap.branches.reduce((acc, branch) => acc + branch.videos.length, 0)) * 100) || 0}%
            </div>
            <div className="text-sm text-gray-500">Complete</div>
          </div>
        </div>
      </div>

      {/* Branches */}
      <div className="space-y-6">
        {roadmap.branches.map((branch) => {
          const branchProgress = calculateBranchProgress(branch);
          
          return (
            <div
              key={branch.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
            >
              {/* Branch Header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {branch.title}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {branch.description}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">
                    {branchProgress}%
                  </div>
                  <div className="text-sm text-gray-500">
                    {formatDuration(branch.estimatedDuration)}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${branchProgress}%` }}
                ></div>
              </div>

              {/* Modules */}
              <div className="space-y-3">
                {branch.videos.map((module) => {
                  const isCompleted = isModuleCompleted(module.id);
                  
                  return (
                    <div
                      key={module.id}
                      className={`flex items-center justify-between p-4 rounded-lg border transition-all duration-200 hover:shadow-md ${
                        isCompleted
                          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                          : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`flex-shrink-0 ${isCompleted ? 'text-green-600' : 'text-gray-400'}`}>
                          {isCompleted ? (
                            <CheckCircle className="h-6 w-6" />
                          ) : (
                            <Play className="h-6 w-6" />
                          )}
                        </div>
                        
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className={`font-medium ${
                              isCompleted 
                                ? 'text-green-800 dark:text-green-200' 
                                : 'text-gray-900 dark:text-white'
                            }`}>
                              {module.title}
                            </h3>
                            {module.isCore && (
                              <Award className="h-4 w-4 text-yellow-500" title="Core module" />
                            )}
                          </div>
                          <div className="flex items-center space-x-3 text-sm text-gray-500">
                            <span>{formatDuration(module.duration)}</span>
                            {module.isCore && (
                              <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded-full text-xs">
                                Core
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        {!isCompleted && (
                          <button
                            onClick={() => markModuleComplete(module.id, branch.id)}
                            className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                          >
                            Mark Complete
                          </button>
                        )}
                        
                        <button
                          onClick={() => setSelectedModule(module)}
                          className="px-3 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors text-sm"
                        >
                          View
                        </button>
                        
                        <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                          <Calendar className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Module Detail Modal */}
      {selectedModule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {selectedModule.title}
                </h3>
                <button
                  onClick={() => setSelectedModule(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                  {selectedModule.videoUrl ? (
                    <iframe
                      src={selectedModule.videoUrl}
                      className="w-full h-full rounded-lg"
                      allowFullScreen
                    ></iframe>
                  ) : (
                    <div className="text-center">
                      <Play className="h-16 w-16 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">Video placeholder</p>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>Duration: {formatDuration(selectedModule.duration)}</span>
                  {selectedModule.isCore && (
                    <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded-full">
                      Core Module
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}