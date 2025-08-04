import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { BookOpen, Zap, Settings, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";

export default function RoadmapCreate() {
  const [userInput, setUserInput] = useState("");
  const [mode, setMode] = useState<"quick" | "detailed" | "custom">("detailed");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const modes = [
    {
      id: "quick" as const,
      name: "Quick Start",
      icon: Zap,
      description: "Fast roadmap generation with essential content",
      detail: "Perfect for getting started quickly with core concepts.",
    },
    {
      id: "detailed" as const,
      name: "Comprehensive",
      icon: BookOpen,
      description: "Detailed roadmap with extensive content",
      detail: "In-depth learning path with comprehensive coverage.",
    },
    {
      id: "custom" as const,
      name: "Customizable",
      icon: Settings,
      description: "Generate roadmap with customization options",
      detail: "Create a roadmap you can modify and tailor to your needs.",
    },
  ];

  const exampleInputs = [
    "Learn full-stack web development with React and Node.js",
    "Master machine learning and data science with Python",
    "Become a DevOps engineer with cloud technologies",
    "Learn mobile app development with React Native",
    "Master system design for senior engineer roles",
  ];

  const generateRoadmap = async () => {
    if (!userInput.trim()) {
      toast.error("Please enter a learning goal");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post("/api/v1/roadmap/generate", {
        user_input: userInput,
        mode: mode === "quick" ? "quick" : "full",
      });

      if (response.data.roadmaps?.length > 0) {
        toast.success("Roadmap generated successfully!");
        navigate(`/roadmap/view?id=${response.data.roadmaps[0].id}`);
      } else {
        toast.error("Failed to generate roadmap");
      }
    } catch (error) {
      console.error("Error generating roadmap:", error);
      toast.error("Failed to generate roadmap");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
          Create Your Learning Roadmap
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mt-4">
          Let AI design a personalized learning path for your goals
        </p>
      </div>

      {/* Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {modes.map((modeOption) => {
          const Icon = modeOption.icon;
          const isActive = mode === modeOption.id;

          return (
            <button
              key={modeOption.id}
              onClick={() => setMode(modeOption.id)}
              className={`text-left p-6 rounded-xl border-2 transition-all duration-200 ${
                isActive
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg"
                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-md"
              }`}
            >
              <div className="flex items-start space-x-4">
                <div
                  className={`p-3 rounded-lg ${
                    isActive ? "bg-blue-500" : "bg-gray-100 dark:bg-gray-700"
                  } text-white`}
                >
                  <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                    {modeOption.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {modeOption.description}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                    {modeOption.detail}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
          What would you like to learn?
        </h2>

        <div className="space-y-4">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-lg"
            placeholder="Describe your learning goals... (e.g., 'Learn full-stack web development with React and Node.js')"
          />

          {/* Example Inputs */}
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Need inspiration? Try one of these:
            </p>
            <div className="flex flex-wrap gap-2">
              {exampleInputs.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setUserInput(example)}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={generateRoadmap}
          disabled={loading || !userInput.trim()}
          className="mt-6 w-full px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 text-lg font-semibold transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></div>
              <span>Generating your roadmap...</span>
            </>
          ) : (
            <>
              <span>Generate Learning Roadmap</span>
              <ArrowRight className="h-6 w-6" />
            </>
          )}
        </button>
      </div>

      {/* Features Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center p-6">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <BookOpen className="h-8 w-8 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            AI-Powered
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Advanced AI creates personalized learning paths tailored to your
            goals
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <Settings className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Customizable
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Modify and adapt your roadmap as you progress and discover new
            interests
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <Zap className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Progress Tracking
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Track your progress and celebrate milestones as you advance
          </p>
        </div>
      </div>
    </div>
  );
}
