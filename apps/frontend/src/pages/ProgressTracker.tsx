import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  Trophy,
  Target,
  Clock,
  BookOpen,
  Award,
  TrendingUp
} from 'lucide-react';

interface ProgressSummary {
  totalModules: number;
  completedModules: number;
  progressPercent: number;
  totalDuration: number;
  completedDuration: number;
  branches: BranchProgress[];
}

interface BranchProgress {
  branchId: string;
  branchTitle: string;
  totalModules: number;
  completedModules: number;
  progressPercent: number;
  estimatedDuration: number;
  completedDuration: number;
}

export default function ProgressTracker() {
  const [progressData, setProgressData] = useState<ProgressSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRoadmap, setSelectedRoadmap] = useState<string>('');
  const [roadmaps, setRoadmaps] = useState<any[]>([]);

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  useEffect(() => {
    if (selectedRoadmap) {
      fetchProgressData();
    }
  }, [selectedRoadmap]);

  const fetchRoadmaps = async () => {
    try {
      const response = await axios.get('/api/v1/roadmap/my-roadmaps');
      setRoadmaps(response.data.roadmaps || []);
      if (response.data.roadmaps?.length > 0) {
        setSelectedRoadmap(response.data.roadmaps[0].id);
      }
    } catch (error) {
      console.error('Error fetching roadmaps:', error);
    }
  };

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/v1/progress/summary?roadmap_id=${selectedRoadmap}`);
      setProgressData(response.data);
    } catch (error) {
      console.error('Error fetching progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const pieChartData = progressData ? [
    { name: 'Completed', value: progressData.completedModules, color: '#10B981' },
    { name: 'Remaining', value: progressData.totalModules - progressData.completedModules, color: '#E5E7EB' }
  ] : [];

  const barChartData = progressData?.branches.map(branch => ({
    name: branch.branchTitle.substring(0, 20) + (branch.branchTitle.length > 20 ? '...' : ''),
    completed: branch.completedModules,
    total: branch.totalModules,
    percentage: branch.progressPercent
  })) || [];

  const motivationalQuotes = [
    "Every expert was once a beginner.",
    "The journey of a thousand miles begins with one step.",
    "Learning never exhausts the mind.",
    "Education is the most powerful weapon to change the world.",
    "The beautiful thing about learning is that no one can take it away from you."
  ];

  const randomQuote = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Progress Tracker
        </h1>
        
        {roadmaps.length > 0 && (
          <select
            value={selectedRoadmap}
            onChange={(e) => setSelectedRoadmap(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            {roadmaps.map((roadmap) => (
              <option key={roadmap.id} value={roadmap.id}>
                {roadmap.title}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Overview Stats */}
      {progressData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Overall Progress</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {Math.round(progressData.progressPercent)}%
                  </p>
                </div>
                <Target className="h-8 w-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Modules Completed</p>
                  <p className="text-3xl font-bold text-green-600">
                    {progressData.completedModules}
                  </p>
                  <p className="text-sm text-gray-500">of {progressData.totalModules}</p>
                </div>
                <BookOpen className="h-8 w-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Study Time</p>
                  <p className="text-3xl font-bold text-purple-600">
                    {formatDuration(progressData.completedDuration)}
                  </p>
                  <p className="text-sm text-gray-500">of {formatDuration(progressData.totalDuration)}</p>
                </div>
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Active Branches</p>
                  <p className="text-3xl font-bold text-orange-600">
                    {progressData.branches.length}
                  </p>
                  <p className="text-sm text-gray-500">learning paths</p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Overall Progress Pie Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Overall Completion
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Branch Progress Bar Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Branch Progress
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="completed" fill="#10B981" name="Completed" />
                    <Bar dataKey="total" fill="#E5E7EB" name="Total" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Branch Details */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Branch Breakdown
              </h3>
              <div className="space-y-4">
                {progressData.branches.map((branch) => (
                  <div key={branch.branchId} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {branch.branchTitle}
                      </h4>
                      <span className="text-sm text-gray-500">
                        {Math.round(branch.progressPercent)}% complete
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${branch.progressPercent}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>
                        {branch.completedModules} of {branch.totalModules} modules
                      </span>
                      <span>
                        {formatDuration(branch.completedDuration)} / {formatDuration(branch.estimatedDuration)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Motivational Section */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-4">
          <Trophy className="h-12 w-12 text-white" />
          <div>
            <h3 className="text-xl font-bold">Keep Going!</h3>
            <p className="text-purple-100 italic">"{randomQuote}"</p>
          </div>
        </div>
      </div>

      {/* Achievement Badges */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Achievements
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <Award className="h-12 w-12 text-yellow-500 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900 dark:text-white">First Module</p>
            <p className="text-xs text-gray-500">Completed your first learning module</p>
          </div>
          
          <div className="text-center">
            <Target className="h-12 w-12 text-blue-500 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900 dark:text-white">50% Progress</p>
            <p className="text-xs text-gray-500">Halfway through your journey</p>
          </div>
          
          <div className="text-center opacity-50">
            <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900 dark:text-white">Completionist</p>
            <p className="text-xs text-gray-500">Complete all modules</p>
          </div>
          
          <div className="text-center opacity-50">
            <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900 dark:text-white">Streak Master</p>
            <p className="text-xs text-gray-500">7-day learning streak</p>
          </div>
        </div>
      </div>

      {!progressData && (
        <div className="text-center py-12">
          <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            No Progress Data
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Start learning to see your progress here.
          </p>
        </div>
      )}
    </div>
  );
}