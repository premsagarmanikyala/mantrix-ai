import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Layout from "./components/Layout";
import LoginForm from "./components/Auth/LoginForm";
import Dashboard from "./pages/Dashboard";
import RoadmapView from "./pages/RoadmapView";
import RoadmapCreate from "./pages/RoadmapCreate";
import ProgressTracker from "./pages/ProgressTracker";
import ResumeBuilder from "./pages/ResumeBuilder";
import RecommendationCenter from "./pages/RecommendationCenter";
import RoadmapMerge from "./pages/RoadmapMerge";
import ExternalRoadmapSearch from "./pages/ExternalRoadmapSearch";
import { Toaster } from "react-hot-toast";

function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <LoginForm />
        <Toaster position="top-right" />
      </>
    );
  }

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Navigate to="/" replace />} />
          <Route path="/roadmap/view" element={<RoadmapView />} />
          <Route path="/roadmap/create" element={<RoadmapCreate />} />
          <Route path="/roadmap/merge" element={<RoadmapMerge />} />
          <Route path="/roadmap/external" element={<ExternalRoadmapSearch />} />
          <Route path="/progress" element={<ProgressTracker />} />
          <Route path="/resume" element={<ResumeBuilder />} />
          <Route path="/recommendations" element={<RecommendationCenter />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
      <Toaster position="top-right" />
    </>
  );
}

export default App;
