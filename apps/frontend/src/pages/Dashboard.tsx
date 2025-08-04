import { useAuth } from "@/hooks/useAuth";
import { Link } from "react-router-dom";
import {
  BookOpen,
  BarChart3,
  FileText,
  Lightbulb,
  Target,
  Clock,
  Award,
  TrendingUp,
  Merge,
} from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();

  const quickActions = [
    {
      title: "Create Roadmap",
      description: "Generate AI-powered learning paths",
      icon: BookOpen,
      href: "/roadmap/create",
      color: "bg-blue-500 hover:bg-blue-600",
    },
    {
      title: "Merge Roadmaps",
      description: "Combine multiple learning paths intelligently",
      icon: Merge,
      href: "/roadmap/merge",
      color: "bg-indigo-500 hover:bg-indigo-600",
    },
    {
      title: "View Progress",
      description: "Track your learning journey",
      icon: BarChart3,
      href: "/progress",
      color: "bg-green-500 hover:bg-green-600",
    },
    {
      title: "Resume Builder",
      description: "Build and analyze your resume",
      icon: FileText,
      href: "/resume",
      color: "bg-purple-500 hover:bg-purple-600",
    },
    {
      title: "Recommendations",
      description: "Get personalized learning suggestions",
      icon: Lightbulb,
      href: "/recommendations",
      color: "bg-yellow-500 hover:bg-yellow-600",
    },
  ];

  const stats = [
    {
      title: "Learning Hours",
      value: "24.5",
      change: "+2.5 this week",
      icon: Clock,
      color: "text-blue-600",
    },
    {
      title: "Completed Modules",
      value: "18",
      change: "+3 this week",
      icon: Target,
      color: "text-green-600",
    },
    {
      title: "Skill Level",
      value: "Intermediate",
      change: "Advanced soon",
      icon: Award,
      color: "text-purple-600",
    },
    {
      title: "Learning Streak",
      value: "7 days",
      change: "Keep it up!",
      icon: TrendingUp,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.firstName || user?.email || "Learner"}!
        </h1>
        <p className="mt-2 text-blue-100">
          Ready to continue your learning journey? Here's what's waiting for
          you.
        </p>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.title}
                to={action.href}
                className={`${action.color} text-white rounded-lg p-6 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{action.title}</h3>
                    <p className="text-sm opacity-90 mt-1">
                      {action.description}
                    </p>
                  </div>
                  <Icon className="h-8 w-8 opacity-80" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Learning Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Your Learning Stats
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.title}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {stat.change}
                    </p>
                  </div>
                  <Icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Continue Learning
        </h2>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    React Advanced Patterns
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Module 3 of 8 • 45 minutes remaining
                  </p>
                </div>
              </div>
              <Link
                to="/roadmap/view"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Continue
              </Link>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    System Design Fundamentals
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Module 1 of 6 • Start your journey
                  </p>
                </div>
              </div>
              <Link
                to="/roadmap/view"
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Start
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Motivational Section */}
      <div className="bg-gradient-to-r from-green-400 to-blue-500 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-4">
          <Award className="h-12 w-12 text-white" />
          <div>
            <h3 className="text-xl font-bold">You're doing great!</h3>
            <p className="text-green-100">
              You've completed 18 modules this month. Keep up the excellent
              work!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
