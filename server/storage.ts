// In-memory storage interface for the application

import {
  User,
  Roadmap,
  ProgressEntry,
  Resume,
  MergedRoadmap,
} from "@shared/schema";

export interface IStorage {
  // User operations
  getUser(id: string): Promise<User | undefined>;
  createUser(user: Omit<User, "id" | "createdAt" | "updatedAt">): Promise<User>;

  // Roadmap operations
  getRoadmap(id: string): Promise<Roadmap | undefined>;
  getUserRoadmaps(userId: string): Promise<Roadmap[]>;
  createRoadmap(
    roadmap: Omit<Roadmap, "id" | "createdAt" | "updatedAt">,
  ): Promise<Roadmap>;

  // Progress operations
  getProgress(userId: string, roadmapId: string): Promise<ProgressEntry[]>;
  addProgress(progress: Omit<ProgressEntry, "id">): Promise<ProgressEntry>;

  // Resume operations
  getResumes(userId: string): Promise<Resume[]>;
  createResume(resume: Omit<Resume, "id" | "createdAt">): Promise<Resume>;

  // Merge operations
  getMergedRoadmap(id: string): Promise<MergedRoadmap | undefined>;
  createMergedRoadmap(
    roadmap: Omit<MergedRoadmap, "id" | "createdAt">,
  ): Promise<MergedRoadmap>;
}

export class MemStorage implements IStorage {
  private users = new Map<string, User>();
  private roadmaps = new Map<string, Roadmap>();
  private progress = new Map<string, ProgressEntry>();
  private resumes = new Map<string, Resume>();
  private mergedRoadmaps = new Map<string, MergedRoadmap>();

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async createUser(
    userData: Omit<User, "id" | "createdAt" | "updatedAt">,
  ): Promise<User> {
    const user: User = {
      ...userData,
      id: `user_${Date.now()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.users.set(user.id, user);
    return user;
  }

  async getRoadmap(id: string): Promise<Roadmap | undefined> {
    return this.roadmaps.get(id);
  }

  async getUserRoadmaps(userId: string): Promise<Roadmap[]> {
    return Array.from(this.roadmaps.values()).filter(
      (r) => r.userId === userId,
    );
  }

  async createRoadmap(
    roadmapData: Omit<Roadmap, "id" | "createdAt" | "updatedAt">,
  ): Promise<Roadmap> {
    const roadmap: Roadmap = {
      ...roadmapData,
      id: `roadmap_${Date.now()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.roadmaps.set(roadmap.id, roadmap);
    return roadmap;
  }

  async getProgress(
    userId: string,
    roadmapId: string,
  ): Promise<ProgressEntry[]> {
    return Array.from(this.progress.values()).filter(
      (p) => p.userId === userId && p.roadmapId === roadmapId,
    );
  }

  async addProgress(
    progressData: Omit<ProgressEntry, "id">,
  ): Promise<ProgressEntry> {
    const progress: ProgressEntry = {
      ...progressData,
      id: `progress_${Date.now()}`,
    };
    this.progress.set(progress.id, progress);
    return progress;
  }

  async getResumes(userId: string): Promise<Resume[]> {
    return Array.from(this.resumes.values()).filter((r) => r.userId === userId);
  }

  async createResume(
    resumeData: Omit<Resume, "id" | "createdAt">,
  ): Promise<Resume> {
    const resume: Resume = {
      ...resumeData,
      id: `resume_${Date.now()}`,
      createdAt: new Date().toISOString(),
    };
    this.resumes.set(resume.id, resume);
    return resume;
  }

  async getMergedRoadmap(id: string): Promise<MergedRoadmap | undefined> {
    return this.mergedRoadmaps.get(id);
  }

  async createMergedRoadmap(
    roadmapData: Omit<MergedRoadmap, "id" | "createdAt">,
  ): Promise<MergedRoadmap> {
    const roadmap: MergedRoadmap = {
      ...roadmapData,
      id: `merged_${Date.now()}`,
      createdAt: new Date().toISOString(),
    };
    this.mergedRoadmaps.set(roadmap.id, roadmap);
    return roadmap;
  }
}

export const storage = new MemStorage();
