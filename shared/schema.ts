// Shared schema definitions for both frontend and backend

export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  profileImageUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Roadmap {
  id: string;
  title: string;
  description?: string;
  estimatedDuration: number;
  branches: RoadmapBranch[];
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface RoadmapBranch {
  id: string;
  title: string;
  description?: string;
  videos: VideoModule[];
  estimatedDuration: number;
}

export interface VideoModule {
  id: string;
  title: string;
  duration: number;
  isCore: boolean;
  description?: string;
}

export interface ProgressEntry {
  id: string;
  userId: string;
  roadmapId: string;
  moduleId: string;
  completedAt: string;
  duration: number;
}

export interface Resume {
  id: string;
  userId: string;
  mode: "study" | "fast" | "analyzer";
  content: string;
  jobDescription?: string;
  atsScore?: number;
  createdAt: string;
}

export interface MergedRoadmap {
  id: string;
  title: string;
  description: string;
  estimatedDuration: number;
  branches: RoadmapBranch[];
  mergedFrom: string[];
  calendar?: Record<string, CalendarEvent[]>;
  userId: string;
  createdAt: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  duration: number;
  isCore: boolean;
  branch_title: string;
  scheduled_time: string;
}
