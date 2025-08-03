import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  BookOpen, 
  TrendingUp, 
  FileText, 
  Lightbulb, 
  Plus, 
  Merge,
  Clock,
  Target,
  Award,
  Brain
} from 'lucide-react'

export default function Dashboard() {
  const { data: progressData } = useQuery({
    queryKey: ['/api/v1/progress/summary'],
  })

  const { data: roadmaps } = useQuery({
    queryKey: ['/api/v1/roadmap/my-roadmaps'],
  })

  const { data: resumes } = useQuery({
    queryKey: ['/api/v1/resume/my-resumes'],
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to Mantrix Learning</h1>
        <p className="text-blue-100">AI-Powered Learning Platform with Multi-Track Merge & Timeline Planning</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <Link to="/roadmap/create" className="block p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Plus className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold">Create Roadmap</h3>
                <p className="text-sm text-muted-foreground">AI-generated learning paths</p>
              </div>
            </div>
          </Link>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <Link to="/roadmap/merge" className="block p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Merge className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold">Merge Roadmaps</h3>
                <p className="text-sm text-muted-foreground">Combine learning tracks</p>
              </div>
            </div>
          </Link>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <Link to="/progress" className="block p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold">Track Progress</h3>
                <p className="text-sm text-muted-foreground">View analytics</p>
              </div>
            </div>
          </Link>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <Link to="/resume" className="block p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                <FileText className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <h3 className="font-semibold">Resume Builder</h3>
                <p className="text-sm text-muted-foreground">Generate AI resumes</p>
              </div>
            </div>
          </Link>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Learning Progress */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Learning Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {progressData ? (
              <>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Overall Completion</span>
                    <span>{progressData.completionPercentage}%</span>
                  </div>
                  <Progress value={progressData.completionPercentage} className="h-2" />
                </div>
                
                <div className="grid grid-cols-3 gap-4 pt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{progressData.completedModules}</div>
                    <div className="text-sm text-muted-foreground">Modules Completed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{progressData.completedHours}h</div>
                    <div className="text-sm text-muted-foreground">Hours Studied</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{progressData.currentStreak}</div>
                    <div className="text-sm text-muted-foreground">Day Streak</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Branch Progress</h4>
                  {progressData.branchProgress?.map((branch: any) => (
                    <div key={branch.branchId} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>{branch.branchTitle}</span>
                        <span>{branch.completed}/{branch.total} modules</span>
                      </div>
                      <Progress value={branch.percentage} className="h-1" />
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Start learning to see your progress</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center gap-3">
                <BookOpen className="h-5 w-5 text-blue-600" />
                <span className="font-medium">Roadmaps</span>
              </div>
              <span className="text-xl font-bold text-blue-600">{roadmaps?.length || 0}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-green-600" />
                <span className="font-medium">Resumes</span>
              </div>
              <span className="text-xl font-bold text-green-600">{resumes?.length || 0}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="flex items-center gap-3">
                <Clock className="h-5 w-5 text-purple-600" />
                <span className="font-medium">Study Hours</span>
              </div>
              <span className="text-xl font-bold text-purple-600">{progressData?.completedHours || 0}h</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Getting Started
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Brain className="h-4 w-4" />
                AI-Powered Features
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Generate personalized learning roadmaps with OpenAI GPT-4</li>
                <li>• Merge multiple tracks with intelligent deduplication</li>
                <li>• Auto-schedule with 30/60/90-day calendar planning</li>
                <li>• Build ATS-optimized resumes from your progress</li>
                <li>• Get AI recommendations based on career goals</li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                Platform Highlights
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Real-time progress tracking and analytics</li>
                <li>• Core video prioritization system</li>
                <li>• Multi-mode resume generation (Study/Fast/Analyzer)</li>
                <li>• Branch-level progress breakdowns</li>
                <li>• Responsive design with dark mode support</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
            <h4 className="font-medium mb-2">Start Your Learning Journey</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Create your first AI-powered roadmap or explore the multi-track merge system.
            </p>
            <div className="flex gap-2">
              <Button asChild size="sm">
                <Link to="/roadmap/create">Create Roadmap</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link to="/roadmap/merge">Merge Tracks</Link>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}