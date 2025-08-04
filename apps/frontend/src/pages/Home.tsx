import { Users, FolderOpen, FileText, Map } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Welcome to Mantrix
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          A comprehensive full-stack monorepo with FastAPI backend and React
          TypeScript frontend
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 py-5 shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="truncate text-sm font-medium text-gray-500 dark:text-gray-400">
                  Users
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  Manage users and profiles
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 py-5 shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FolderOpen className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="truncate text-sm font-medium text-gray-500 dark:text-gray-400">
                  Projects
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  Track and manage projects
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 py-5 shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="truncate text-sm font-medium text-gray-500 dark:text-gray-400">
                  Resume Builder
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  AI-powered resume generation
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 py-5 shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Map className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="truncate text-sm font-medium text-gray-500 dark:text-gray-400">
                  Roadmap Engine
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  Generate learning roadmaps
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-lg bg-white dark:bg-gray-800 p-6 shadow">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Project Architecture
        </h2>
        <div className="prose dark:prose-invert max-w-none">
          <ul className="space-y-2">
            <li>
              <strong>Backend:</strong> FastAPI with Python 3.11, SQLAlchemy,
              Pydantic
            </li>
            <li>
              <strong>Frontend:</strong> React 18 with TypeScript, Tailwind CSS,
              React Query
            </li>
            <li>
              <strong>Database:</strong> PostgreSQL (configurable)
            </li>
            <li>
              <strong>Infrastructure:</strong> Docker, GitHub Actions CI/CD
            </li>
            <li>
              <strong>AI Services:</strong> Resume builder and roadmap
              generation engines
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
