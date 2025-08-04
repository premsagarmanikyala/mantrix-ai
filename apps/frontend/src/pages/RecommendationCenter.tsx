import { useState } from "react";
import axios from "axios";
import {
  Lightbulb,
  Target,
  FileText,
  Brain,
  Plus,
  Clock,
  Star,
  CheckCircle,
  TrendingUp,
} from "lucide-react";

interface RecommendedModule {
  title: string;
  duration: number;
  difficulty: string;
  priority: number;
}

interface RecommendedBranch {
  id: string;
  title: string;
  reason: string;
  estimatedDuration: number;
  difficulty: string;
  prerequisites: string[];
  modules: RecommendedModule[];
  completionBenefit: string;
}

interface Recommendation {
  recommendations: RecommendedBranch[];
  analysisSSummary: string;
  confidenceScore: number;
  nextSteps: string[];
  mode: string;
}

export default function RecommendationCenter() {
  const [activeMode, setActiveMode] = useState<"gap" | "resume" | "interest">(
    "gap",
  );
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [newInterest, setNewInterest] = useState("");
  const [recommendations, setRecommendations] = useState<Recommendation | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const modes = [
    {
      id: "gap" as const,
      name: "Gap Analysis",
      icon: Target,
      description: "Analyze skills needed for target job roles",
      color: "bg-blue-500 hover:bg-blue-600",
      detail:
        "Compare your current skills with job requirements to identify learning gaps.",
    },
    {
      id: "resume" as const,
      name: "Resume Enhancement",
      icon: FileText,
      description: "Suggest improvements to enhance your profile",
      color: "bg-green-500 hover:bg-green-600",
      detail:
        "Get suggestions to strengthen your resume and professional profile.",
    },
    {
      id: "interest" as const,
      name: "Interest-Based",
      icon: Brain,
      description: "Personalized paths from your interests",
      color: "bg-purple-500 hover:bg-purple-600",
      detail:
        "Discover learning paths based on your interests and career goals.",
    },
  ];

  const commonInterests = [
    "Machine Learning",
    "Data Science",
    "Web Development",
    "Mobile Development",
    "Cloud Computing",
    "DevOps",
    "Cybersecurity",
    "UI/UX Design",
    "Blockchain",
    "AI/ML",
    "System Design",
    "Leadership",
  ];

  const addInterest = () => {
    if (newInterest && !interests.includes(newInterest)) {
      setInterests([...interests, newInterest]);
      setNewInterest("");
    }
  };

  const removeInterest = (interest: string) => {
    setInterests(interests.filter((i) => i !== interest));
  };

  const addCommonInterest = (interest: string) => {
    if (!interests.includes(interest)) {
      setInterests([...interests, interest]);
    }
  };

  const generateRecommendations = async () => {
    try {
      setLoading(true);
      const requestData: any = { mode: activeMode };

      if (activeMode === "gap" && jobDescription) {
        requestData.target_job_description = jobDescription;
      } else if (activeMode === "resume" && resume) {
        requestData.existing_resume = resume;
      } else if (activeMode === "interest") {
        requestData.skill_interests = interests;
      }

      const response = await axios.post(
        "/api/v1/roadmap/recommend",
        requestData,
      );
      setRecommendations(response.data);
    } catch (error) {
      console.error("Error generating recommendations:", error);
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

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case "beginner":
        return "text-green-600 bg-green-100 dark:bg-green-900/30";
      case "intermediate":
        return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30";
      case "advanced":
        return "text-red-600 bg-red-100 dark:bg-red-900/30";
      default:
        return "text-gray-600 bg-gray-100 dark:bg-gray-900/30";
    }
  };

  const addToRoadmap = async (branchId: string) => {
    try {
      // This would integrate with the roadmap creation API
      console.log("Adding branch to roadmap:", branchId);
      // Show success message
    } catch (error) {
      console.error("Error adding to roadmap:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Recommendation Center
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Get AI-powered learning recommendations tailored to your goals
        </p>
      </div>

      {/* Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = activeMode === mode.id;

          return (
            <button
              key={mode.id}
              onClick={() => setActiveMode(mode.id)}
              className={`text-left p-6 rounded-lg border-2 transition-all duration-200 ${
                isActive
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
              }`}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${mode.color} text-white`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {mode.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {mode.description}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                    {mode.detail}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Get Recommendations - {modes.find((m) => m.id === activeMode)?.name}
        </h2>

        {activeMode === "gap" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Paste the job description you're targeting..."
            />
          </div>
        )}

        {activeMode === "resume" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Resume
            </label>
            <textarea
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Paste your current resume content..."
            />
          </div>
        )}

        {activeMode === "interest" && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Your Interests
              </label>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && addInterest()}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Add an interest..."
                />
                <button
                  onClick={addInterest}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-1"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add</span>
                </button>
              </div>

              {interests.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {interests.map((interest) => (
                    <span
                      key={interest}
                      className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm flex items-center space-x-1"
                    >
                      <span>{interest}</span>
                      <button
                        onClick={() => removeInterest(interest)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}

              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Or choose from common interests:
                </p>
                <div className="flex flex-wrap gap-2">
                  {commonInterests.map((interest) => (
                    <button
                      key={interest}
                      onClick={() => addCommonInterest(interest)}
                      disabled={interests.includes(interest)}
                      className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                        interests.includes(interest)
                          ? "bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed"
                          : "border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={generateRecommendations}
          disabled={
            loading ||
            (activeMode === "gap" && !jobDescription) ||
            (activeMode === "resume" && !resume)
          }
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Lightbulb className="h-4 w-4" />
              <span>Get Recommendations</span>
            </>
          )}
        </button>
      </div>

      {/* Recommendations Results */}
      {recommendations && (
        <div className="space-y-6">
          {/* Analysis Summary */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Analysis Summary
              </h2>
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span className="font-semibold text-gray-900 dark:text-white">
                  {Math.round(recommendations.confidenceScore * 100)}%
                  Confidence
                </span>
              </div>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              {recommendations.analysisSSummary}
            </p>
          </div>

          {/* Recommended Learning Paths */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Recommended Learning Paths
            </h2>

            {recommendations.recommendations.map((branch) => (
              <div
                key={branch.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {branch.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                      {branch.reason}
                    </p>
                    <div className="flex items-center space-x-4 mt-3">
                      <div className="flex items-center text-gray-500">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{formatDuration(branch.estimatedDuration)}</span>
                      </div>
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(branch.difficulty)}`}
                      >
                        {branch.difficulty}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => addToRoadmap(branch.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add to Roadmap</span>
                  </button>
                </div>

                {branch.prerequisites.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Prerequisites:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {branch.prerequisites.map((prereq) => (
                        <span
                          key={prereq}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded"
                        >
                          {prereq}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Learning Modules:
                  </h4>
                  {branch.modules.map((module, moduleIndex) => (
                    <div
                      key={moduleIndex}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                          {moduleIndex + 1}
                        </div>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {module.title}
                        </span>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-gray-500">
                        <span>{formatDuration(module.duration)}</span>
                        <span
                          className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(module.difficulty)}`}
                        >
                          {module.difficulty}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0" />
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-green-800 dark:text-green-200">
                        What you'll gain:
                      </h4>
                      <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                        {branch.completionBenefit}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Next Steps */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Next Steps
            </h3>
            <div className="space-y-3">
              {recommendations.nextSteps.map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!recommendations && !loading && (
        <div className="text-center py-12">
          <Lightbulb className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Ready for Recommendations
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Choose a mode above and provide the required information to get
            personalized learning recommendations.
          </p>
        </div>
      )}
    </div>
  );
}
