import { useState, useEffect } from "react";
import axios from "axios";
import {
  FileText,
  Zap,
  Search,
  Download,
  Eye,
  Edit3,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

interface Resume {
  id: string;
  mode: "study" | "fast" | "analyzer";
  content: string;
  atsScore?: number;
  feedback?: string;
  createdAt: string;
}

export default function ResumeBuilder() {
  const [activeMode, setActiveMode] = useState<"study" | "fast" | "analyzer">(
    "fast",
  );
  const [resumeContent, setResumeContent] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const response = await axios.get("/api/v1/resume/my-resumes");
      setResumes(response.data.resumes || []);
    } catch (error) {
      console.error("Error fetching resumes:", error);
    }
  };

  const generateResume = async () => {
    try {
      setLoading(true);
      const requestData: any = { mode: activeMode };

      if (activeMode === "analyzer" && resumeContent && jobDescription) {
        requestData.existing_resume = resumeContent;
        requestData.job_description = jobDescription;
      } else if (activeMode === "study") {
        // Study mode uses completed modules only
      } else {
        // Fast mode uses full roadmap content
      }

      const response = await axios.post("/api/v1/resume/generate", requestData);
      setResult(response.data);
      await fetchResumes();
    } catch (error) {
      console.error("Error generating resume:", error);
    } finally {
      setLoading(false);
    }
  };

  const modes = [
    {
      id: "study" as const,
      name: "Study Mode",
      icon: FileText,
      description: "Resume based on completed modules only",
      color: "bg-blue-500 hover:bg-blue-600",
      detail:
        "Generate a resume showcasing skills from modules you've actually completed.",
    },
    {
      id: "fast" as const,
      name: "Fast Mode",
      icon: Zap,
      description: "Full roadmap content resume generation",
      color: "bg-green-500 hover:bg-green-600",
      detail:
        "Create a comprehensive resume including all your planned learning paths.",
    },
    {
      id: "analyzer" as const,
      name: "Analyzer Mode",
      icon: Search,
      description: "Resume vs job description analysis with ATS scoring",
      color: "bg-purple-500 hover:bg-purple-600",
      detail:
        "Analyze your resume against a job description with ATS compatibility scoring.",
    },
  ];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return CheckCircle;
    if (score >= 60) return AlertCircle;
    return AlertCircle;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Resume Builder
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Create professional resumes with AI-powered optimization
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
          Generate Resume - {modes.find((m) => m.id === activeMode)?.name}
        </h2>

        {activeMode === "analyzer" && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Current Resume
              </label>
              <textarea
                value={resumeContent}
                onChange={(e) => setResumeContent(e.target.value)}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Paste your current resume content here..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Paste the job description you're targeting..."
              />
            </div>
          </div>
        )}

        {activeMode !== "analyzer" && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-blue-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Ready to Generate
                </h3>
                <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                  <p>
                    {activeMode === "study"
                      ? "We'll create a resume based on your completed learning modules and verified skills."
                      : "We'll generate a comprehensive resume including all your learning paths and planned skills."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={generateResume}
          disabled={
            loading ||
            (activeMode === "analyzer" && (!resumeContent || !jobDescription))
          }
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <FileText className="h-4 w-4" />
              <span>Generate Resume</span>
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Generated Resume
            </h2>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 flex items-center space-x-1">
                <Eye className="h-4 w-4" />
                <span>Preview</span>
              </button>
              <button className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-1">
                <Download className="h-4 w-4" />
                <span>Download</span>
              </button>
            </div>
          </div>

          {result.ats_score && (
            <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900 dark:text-white">
                  ATS Compatibility Score
                </h3>
                <div className="flex items-center space-x-2">
                  {(() => {
                    const ScoreIcon = getScoreIcon(result.ats_score);
                    return (
                      <ScoreIcon
                        className={`h-5 w-5 ${getScoreColor(result.ats_score)}`}
                      />
                    );
                  })()}
                  <span
                    className={`text-2xl font-bold ${getScoreColor(result.ats_score)}`}
                  >
                    {result.ats_score}%
                  </span>
                </div>
              </div>
              {result.feedback && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  {result.feedback}
                </p>
              )}
            </div>
          )}

          <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
              {result.resume_content}
            </pre>
          </div>
        </div>
      )}

      {/* Recent Resumes */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Resumes
        </h2>

        {resumes.length > 0 ? (
          <div className="space-y-3">
            {resumes.slice(0, 5).map((resume) => (
              <div
                key={resume.id}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <div className="flex items-center space-x-4">
                  <div
                    className={`p-2 rounded-lg ${
                      resume.mode === "study"
                        ? "bg-blue-500"
                        : resume.mode === "fast"
                          ? "bg-green-500"
                          : "bg-purple-500"
                    } text-white`}
                  >
                    {resume.mode === "study" ? (
                      <FileText className="h-4 w-4" />
                    ) : resume.mode === "fast" ? (
                      <Zap className="h-4 w-4" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {resume.mode.charAt(0).toUpperCase() +
                        resume.mode.slice(1)}{" "}
                      Mode Resume
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatDate(resume.createdAt)}
                      {resume.atsScore && (
                        <span
                          className={`ml-2 ${getScoreColor(resume.atsScore)}`}
                        >
                          • ATS Score: {resume.atsScore}%
                        </span>
                      )}
                    </p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              No resumes yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Generate your first AI-powered resume above.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
