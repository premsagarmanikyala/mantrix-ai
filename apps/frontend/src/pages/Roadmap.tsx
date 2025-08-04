import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Map, Clock, BookOpen, FolderOpen } from "lucide-react";
// Update this import to match the actual exports from '@/lib/api'
import { api } from "@/lib/api";
// import projectApi from '@/lib/api' // Uncomment and adjust if projectApi is a default export

export default function Roadmap() {
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(
    null,
  );
  const [skillLevel, setSkillLevel] = useState("beginner");
  const [timeframe, setTimeframe] = useState("3_months");
  const [generatedRoadmap, setGeneratedRoadmap] = useState<any>(null);

  const { data: projects = [] } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.get("/projects").then((res) => res.data),
  });

  const generateMutation = useMutation({
    mutationFn: (projectId: number) => api.post("/roadmap", { projectId }),
    onSuccess: () => {
      // In a real app, this would return the actual roadmap data
      setGeneratedRoadmap({
        projectId: selectedProjectId,
        skillLevel,
        timeframe,
        status: "generated",
        createdAt: new Date().toISOString(),
        milestones: [
          {
            week: 1,
            title: "Project Setup & Planning",
            description:
              "Define requirements and set up development environment",
          },
          {
            week: 3,
            title: "Core Development - Phase 1",
            description: "Implement basic functionality and core features",
          },
          {
            week: 6,
            title: "Core Development - Phase 2",
            description: "Add advanced features and integrations",
          },
          {
            week: 9,
            title: "Testing & Optimization",
            description: "Comprehensive testing and performance optimization",
          },
          {
            week: 12,
            title: "Deployment & Documentation",
            description: "Deploy to production and complete documentation",
          },
        ],
        estimatedHours:
          timeframe === "1_month"
            ? 40
            : timeframe === "3_months"
              ? 120
              : timeframe === "6_months"
                ? 240
                : 480,
      });
    },
  });

  const handleGenerate = () => {
    if (selectedProjectId) {
      generateMutation.mutate(selectedProjectId);
    }
  };

  interface Project {
    id: number;
    title: string;
    status: string;
    priority: string;
    description?: string;
  }

  interface Milestone {
    week: number;
    title: string;
    description: string;
  }

  const selectedProject: Project | undefined = projects.find(
    (p: Project) => p.id === selectedProjectId,
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Roadmap Engine
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          Generate personalized learning roadmaps for your projects
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Project Selection */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Select Project
            </h2>

            <div className="space-y-3">
              {projects.map((project: Project) => (
                <div
                  key={project.id}
                  onClick={() => setSelectedProjectId(project.id)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    selectedProjectId === project.id
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <FolderOpen className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {project.title}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {project.status} • {project.priority} priority
                      </p>
                      {project.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                          {project.description}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Configuration Options */}
          {selectedProjectId && (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Roadmap Configuration
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Skill Level
                  </label>
                  <select
                    value={skillLevel}
                    onChange={(e) => setSkillLevel(e.target.value)}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Timeframe
                  </label>
                  <select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="1_month">1 Month</option>
                    <option value="3_months">3 Months</option>
                    <option value="6_months">6 Months</option>
                    <option value="1_year">1 Year</option>
                  </select>
                </div>

                <button
                  onClick={handleGenerate}
                  disabled={generateMutation.isPending}
                  className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <Map className="h-4 w-4 mr-2" />
                  {generateMutation.isPending
                    ? "Generating..."
                    : "Generate Roadmap"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Roadmap Display */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Learning Roadmap
          </h2>

          {!generatedRoadmap && !selectedProject && (
            <div className="text-center py-12">
              <Map className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                No roadmap generated
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Select a project and configure your preferences to generate a
                roadmap.
              </p>
            </div>
          )}

          {selectedProject && !generatedRoadmap && (
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
              <div className="text-center">
                <Map className="mx-auto h-8 w-8 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                  Ready to generate roadmap for "{selectedProject.title}"
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Configure your preferences and click generate to create a
                  learning roadmap.
                </p>
              </div>
            </div>
          )}

          {generatedRoadmap && selectedProject && (
            <div className="space-y-6">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <Map className="h-5 w-5 text-green-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
                      Roadmap Generated Successfully
                    </h3>
                    <div className="mt-2 text-sm text-green-700 dark:text-green-300">
                      <p>
                        Learning roadmap for "{selectedProject.title}" has been
                        generated.
                      </p>
                      <p className="mt-1">
                        Skill Level: {skillLevel} • Timeframe:{" "}
                        {timeframe.replace("_", " ")} • Estimated Hours:{" "}
                        {generatedRoadmap.estimatedHours}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-gray-900 dark:text-white">
                  Milestones:
                </h4>
                {generatedRoadmap.milestones.map(
                  (milestone: any, index: number) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                    >
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600 dark:text-blue-300">
                            {milestone.week}
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                          Week {milestone.week}: {milestone.title}
                        </h5>
                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                          {milestone.description}
                        </p>
                      </div>
                    </div>
                  ),
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div className="text-center">
                  <Clock className="mx-auto h-6 w-6 text-gray-400 mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {generatedRoadmap.estimatedHours} Hours
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Total Time
                  </p>
                </div>
                <div className="text-center">
                  <BookOpen className="mx-auto h-6 w-6 text-gray-400 mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {generatedRoadmap.milestones.length} Milestones
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Learning Steps
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
