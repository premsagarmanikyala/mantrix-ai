import { Hono } from "hono";
import { cors } from "hono/cors";
import { storage } from "./storage";
import type { User, Roadmap, MergedRoadmap } from "@shared/schema";

const app = new Hono();

// Enable CORS
app.use("/api/*", cors());

// Health check
app.get("/health", (c) => {
  return c.json({ status: "healthy", service: "mantrix-learning-platform" });
});

// Auth endpoints (simplified for demo)
app.post("/api/auth/login", async (c) => {
  const { email, password } = await c.req.json();

  // For demo purposes, create or find user by email
  const users = await storage.getUserRoadmaps("demo"); // Get all users
  let user = users.find((u) => u.userId === email); // Find by email

  if (!user) {
    // Create demo user
    const newUser = await storage.createUser({
      email,
      firstName: "Demo",
      lastName: "User",
    });
    user = newUser as any;
  }

  return c.json({
    user: { id: user.userId || email, email, firstName: "Demo" },
    token: `demo_token_${Date.now()}`,
  });
});

app.get("/api/auth/me", (c) => {
  const auth = c.req.header("Authorization");
  if (!auth) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  return c.json({
    id: "demo_user",
    email: "demo@example.com",
    firstName: "Demo",
    lastName: "User",
  });
});

// Roadmap endpoints
app.get("/api/v1/roadmap/my-roadmaps", async (c) => {
  const roadmaps = await storage.getUserRoadmaps("demo_user");
  return c.json(roadmaps);
});

app.post("/api/v1/roadmap/generate", async (c) => {
  const { user_input } = await c.req.json();

  // Generate sample roadmap
  const roadmap = await storage.createRoadmap({
    title: `Learning Path: ${user_input}`,
    description: `AI-generated roadmap for ${user_input}`,
    estimatedDuration: 7200, // 2 hours
    branches: [
      {
        id: "branch_1",
        title: "Fundamentals",
        description: "Core concepts and basics",
        estimatedDuration: 3600,
        videos: [
          {
            id: "video_1",
            title: "Introduction",
            duration: 900,
            isCore: true,
            description: "Getting started basics",
          },
          {
            id: "video_2",
            title: "Core Concepts",
            duration: 1200,
            isCore: true,
            description: "Essential principles",
          },
        ],
      },
      {
        id: "branch_2",
        title: "Advanced Topics",
        description: "Deep dive into advanced areas",
        estimatedDuration: 3600,
        videos: [
          {
            id: "video_3",
            title: "Advanced Techniques",
            duration: 1800,
            isCore: false,
            description: "Professional level skills",
          },
        ],
      },
    ],
    userId: "demo_user",
  });

  return c.json({
    roadmap,
    status: "success",
    message: "Roadmap generated successfully",
  });
});

// Merge endpoints
app.get("/api/v1/roadmap/mergeable", async (c) => {
  const roadmaps = await storage.getUserRoadmaps("demo_user");
  return c.json(
    roadmaps.map((r) => ({
      id: r.id,
      title: r.title,
      description: r.description || "",
      estimatedDuration: r.estimatedDuration,
      branchCount: r.branches.length,
    })),
  );
});

app.post("/api/v1/roadmap/merge/preview", async (c) => {
  const { roadmap_ids } = await c.req.json();

  const roadmaps = await Promise.all(
    roadmap_ids.map((id: string) => storage.getRoadmap(id)),
  );

  const validRoadmaps = roadmaps.filter(Boolean) as Roadmap[];

  const mergedTitle = `Merged: ${validRoadmaps.map((r) => r.title).join(" + ")}`;
  const totalDuration = validRoadmaps.reduce(
    (sum, r) => sum + r.estimatedDuration,
    0,
  );
  const allBranches = validRoadmaps.flatMap((r) => r.branches);

  // Simple deduplication by title
  const uniqueBranches = allBranches.filter(
    (branch, index) =>
      allBranches.findIndex((b) => b.title === branch.title) === index,
  );

  const optimizedDuration = uniqueBranches.reduce(
    (sum, b) => sum + b.estimatedDuration,
    0,
  );
  const durationSaved = totalDuration - optimizedDuration;

  return c.json({
    preview: {
      id: "preview",
      title: mergedTitle,
      description: `Intelligent merge of ${validRoadmaps.length} learning tracks`,
      estimatedDuration: optimizedDuration,
      branches: uniqueBranches,
    },
    statistics: {
      original_roadmaps: validRoadmaps.length,
      original_duration: totalDuration,
      final_duration: optimizedDuration,
      duration_saved: durationSaved,
      original_branches: allBranches.length,
      final_branches: uniqueBranches.length,
      efficiency_gain: Math.round((durationSaved / totalDuration) * 100) || 0,
    },
  });
});

app.post("/api/v1/roadmap/merge", async (c) => {
  const { roadmap_ids, schedule_mode, calendar_view, daily_study_hours } =
    await c.req.json();

  // Get preview data
  const previewResponse = await app.request("/api/v1/roadmap/merge/preview", {
    method: "POST",
    body: JSON.stringify({ roadmap_ids }),
    headers: { "Content-Type": "application/json" },
  });

  const { preview } = await previewResponse.json();

  // Generate calendar if requested
  let calendar = undefined;
  if (schedule_mode === "auto" && calendar_view) {
    calendar = generateAutoSchedule(preview, daily_study_hours || 1.0);
  }

  // Save merged roadmap
  const mergedRoadmap = await storage.createMergedRoadmap({
    title: preview.title,
    description: preview.description,
    estimatedDuration: preview.estimatedDuration,
    branches: preview.branches,
    mergedFrom: roadmap_ids,
    calendar,
    userId: "demo_user",
  });

  return c.json({
    merged_roadmap: { ...mergedRoadmap, calendar },
    source_count: roadmap_ids.length,
    schedule_mode,
    calendar_enabled: calendar_view,
  });
});

// Progress endpoints
app.post("/api/v1/progress/complete", async (c) => {
  const { roadmap_id, module_id, duration } = await c.req.json();

  const progress = await storage.addProgress({
    userId: "demo_user",
    roadmapId: roadmap_id,
    moduleId: module_id,
    completedAt: new Date().toISOString(),
    duration: duration || 0,
  });

  return c.json({
    progress,
    status: "success",
    message: "Module completed successfully",
  });
});

app.get("/api/v1/progress/summary", async (c) => {
  // Return sample progress data
  return c.json({
    totalModules: 15,
    completedModules: 8,
    totalHours: 12.5,
    completedHours: 6.2,
    completionPercentage: 53,
    currentStreak: 7,
    branchProgress: [
      {
        branchId: "branch_1",
        branchTitle: "Fundamentals",
        completed: 5,
        total: 7,
        percentage: 71,
      },
      {
        branchId: "branch_2",
        branchTitle: "Advanced Topics",
        completed: 3,
        total: 8,
        percentage: 38,
      },
    ],
  });
});

// Resume endpoints
app.post("/api/v1/resume/generate", async (c) => {
  const { mode, content, job_description } = await c.req.json();

  const resume = await storage.createResume({
    userId: "demo_user",
    mode,
    content:
      content || "Generated resume content based on your learning progress...",
    jobDescription: job_description,
    atsScore:
      mode === "analyzer" ? Math.floor(Math.random() * 40) + 60 : undefined,
  });

  return c.json({
    resume,
    status: "success",
    message: "Resume generated successfully",
  });
});

app.get("/api/v1/resume/my-resumes", async (c) => {
  const resumes = await storage.getResumes("demo_user");
  return c.json(resumes);
});

// Recommendation endpoints
app.post("/api/v1/roadmap/recommend", async (c) => {
  const { mode, input } = await c.req.json();

  return c.json({
    recommendations: [
      {
        id: "rec_1",
        title: "Advanced JavaScript Patterns",
        description:
          "Enhance your JavaScript skills with advanced design patterns",
        confidence: 0.85,
        modules: ["Closures & Scope", "Prototype Chain", "Async Patterns"],
        estimatedDuration: 4800,
      },
      {
        id: "rec_2",
        title: "React Performance Optimization",
        description: "Learn to build high-performance React applications",
        confidence: 0.78,
        modules: ["Memoization", "Code Splitting", "Bundle Optimization"],
        estimatedDuration: 3600,
      },
    ],
    mode,
    status: "success",
  });
});

// External roadmap API endpoints
app.get("/api/v1/external-roadmaps/sources", async (c) => {
  return c.json([
    {
      id: "github_awesome",
      name: "GitHub Awesome Lists", 
      description: "Community-curated learning roadmaps from GitHub",
      base_url: "https://api.github.com/repos",
      is_active: true
    },
    {
      id: "roadmap_sh",
      name: "Roadmap.sh",
      description: "Developer roadmaps for various technologies", 
      base_url: "https://roadmap.sh/roadmaps",
      is_active: true
    },
    {
      id: "freecodecamp",
      name: "FreeCodeCamp",
      description: "Free coding bootcamp curriculum roadmaps",
      base_url: "https://api.freecodecamp.org",
      is_active: true
    }
  ]);
});

app.get("/api/v1/external-roadmaps/search", async (c) => {
  const { query, sources } = c.req.query();
  
  if (!query) {
    return c.json({ error: "Query parameter is required" }, 400);
  }

  // Simulate external roadmap search results
  const sampleRoadmaps = [
    {
      id: "roadmapsh_frontend",
      title: "Frontend Developer Roadmap",
      description: "Step-by-step guide to becoming a modern frontend developer",
      source: "Roadmap.sh",
      source_url: "https://roadmap.sh/frontend",
      topics: ["html", "css", "javascript", "react", "vue"],
      difficulty: "Beginner to Advanced",
      estimated_duration: 500,
      steps: [
        {
          title: "Learn HTML",
          description: "Semantic HTML and accessibility",
          type: "learning",
          estimated_time: 40
        },
        {
          title: "Learn CSS", 
          description: "Styling, layouts, and responsive design",
          type: "learning",
          estimated_time: 60
        },
        {
          title: "Learn JavaScript",
          description: "Programming fundamentals and DOM manipulation", 
          type: "learning",
          estimated_time: 120
        }
      ]
    },
    {
      id: "fcc_javascript",
      title: "FreeCodeCamp: JavaScript Algorithms and Data Structures",
      description: "Learn JavaScript fundamentals and algorithmic thinking",
      source: "FreeCodeCamp",
      source_url: "https://www.freecodecamp.org/learn/javascript",
      topics: ["javascript", "algorithms", "data-structures"],
      difficulty: "Beginner",
      estimated_duration: 600,
      steps: [
        {
          title: "Basic JavaScript",
          description: "Variables, functions, and control flow",
          type: "interactive", 
          estimated_time: 180
        },
        {
          title: "ES6",
          description: "Modern JavaScript features",
          type: "interactive",
          estimated_time: 120
        }
      ]
    }
  ].filter(roadmap => 
    roadmap.title.toLowerCase().includes(query.toLowerCase()) ||
    roadmap.topics.some(topic => topic.toLowerCase().includes(query.toLowerCase()))
  );

  return c.json({
    roadmaps: sampleRoadmaps,
    query,
    sources_searched: sources ? sources.split(",") : ["github_awesome", "roadmap_sh", "freecodecamp"],
    total_found: sampleRoadmaps.length,
    status: "success"
  });
});

app.post("/api/v1/external-roadmaps/search", async (c) => {
  const { query, sources, limit } = await c.req.json();
  
  if (!query) {
    return c.json({ error: "Query is required" }, 400);
  }

  // Reuse the GET logic
  const searchResult = await app.request("/api/v1/external-roadmaps/search?query=" + encodeURIComponent(query));
  const data = await searchResult.json();
  
  // Apply limit if specified
  if (limit && data.roadmaps) {
    data.roadmaps = data.roadmaps.slice(0, limit);
  }
  
  return c.json(data);
});

app.get("/api/v1/external-roadmaps/health", (c) =>
  c.json({ 
    status: "healthy", 
    service: "external-roadmaps",
    active_sources: ["github_awesome", "roadmap_sh", "freecodecamp"],
    total_sources: 3,
    test_search_working: true
  })
);

// Health checks for all services
app.get("/api/v1/roadmap/health", (c) =>
  c.json({ status: "healthy", service: "roadmap" }),
);
app.get("/api/v1/roadmap/merge/health", (c) =>
  c.json({ status: "healthy", service: "roadmap-merge" }),
);
app.get("/api/v1/resume/health", (c) =>
  c.json({ status: "healthy", service: "resume" }),
);
app.get("/api/v1/progress/health", (c) =>
  c.json({ status: "healthy", service: "progress" }),
);
app.get("/api/v1/external-roadmaps/health", (c) =>
  c.json({ status: "healthy", service: "external-roadmaps" }),
);

// Helper function for auto scheduling
function generateAutoSchedule(roadmap: any, dailyHours: number) {
  const calendar: Record<string, any[]> = {};
  const dailySeconds = dailyHours * 3600;
  let currentDate = new Date();

  // Get all videos from all branches
  const allVideos = roadmap.branches.flatMap((branch: any) =>
    branch.videos.map((video: any) => ({
      ...video,
      branch_title: branch.title,
    })),
  );

  // Sort core videos first
  allVideos.sort((a, b) => (b.isCore ? 1 : 0) - (a.isCore ? 1 : 0));

  let videoIndex = 0;
  let dayOffset = 0;

  while (videoIndex < allVideos.length && dayOffset < 30) {
    const scheduleDate = new Date(currentDate);
    scheduleDate.setDate(scheduleDate.getDate() + dayOffset);

    // Skip weekends
    if (scheduleDate.getDay() === 0 || scheduleDate.getDay() === 6) {
      dayOffset++;
      continue;
    }

    const dateStr = scheduleDate.toISOString().split("T")[0];
    const dailyVideos = [];
    let dailyDuration = 0;

    while (videoIndex < allVideos.length && dailyDuration < dailySeconds) {
      const video = allVideos[videoIndex];
      if (dailyDuration + video.duration <= dailySeconds) {
        dailyVideos.push({
          ...video,
          scheduled_time: "09:00",
        });
        dailyDuration += video.duration;
        videoIndex++;
      } else {
        break;
      }
    }

    if (dailyVideos.length > 0) {
      calendar[dateStr] = dailyVideos;
    }

    dayOffset++;
  }

  return calendar;
}

export default app;
