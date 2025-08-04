import { useToast } from "@/hooks/use-toast";
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Merge, 
  Calendar, 
  Clock, 
  Users, 
  BookOpen, 
  TrendingUp, 
  CheckCircle,
  Star,
  Eye,
  Plus,
  Shuffle
} from 'lucide-react';

interface MergeableRoadmap {
  id: string;
  title: string;
  description: string;
  estimatedDuration: number;
  branchCount: number;
}

interface MergePreview {
  preview: {
    id: string;
    title: string;
    description: string;
    estimatedDuration: number;
    branches: any[];
  };
  statistics: {
    original_roadmaps: number;
    original_duration: number;
    final_duration: number;
    duration_saved: number;
    original_branches: number;
    final_branches: number;
    efficiency_gain: number;
  };
}

interface CalendarEvent {
  id: string;
  title: string;
  duration: number;
  isCore: boolean;
  branch_title: string;
  scheduled_time: string;
}

const RoadmapMerge: React.FC = () => {
  const [mergeableRoadmaps, setMergeableRoadmaps] = useState<MergeableRoadmap[]>([]);
  const [selectedRoadmaps, setSelectedRoadmaps] = useState<string[]>([]);
  const [scheduleMode, setScheduleMode] = useState<'none' | 'auto' | 'manual'>('none');
  const [calendarView, setCalendarView] = useState(false);
  const [dailyStudyHours, setDailyStudyHours] = useState(1.0);
  const [mergePreview, setMergePreview] = useState<MergePreview | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mergedRoadmap, setMergedRoadmap] = useState(null);
  const [calendarData, setCalendarData] = useState<Record<string, CalendarEvent[]>>({});
  const { toast } = useToast();

  useEffect(() => {
    fetchMergeableRoadmaps();
  }, []);

  const fetchMergeableRoadmaps = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('/api/v1/roadmap/mergeable', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setMergeableRoadmaps(data);
      }
    } catch (error) {
      console.error('Error fetching mergeable roadmaps:', error);
    }
  };

  const handleRoadmapSelection = (roadmapId: string, selected: boolean) => {
    if (selected) {
      setSelectedRoadmaps([...selectedRoadmaps, roadmapId]);
    } else {
      setSelectedRoadmaps(selectedRoadmaps.filter(id => id !== roadmapId));
    }
  };

  const generatePreview = async () => {
    if (selectedRoadmaps.length < 2) {
      toast({
        title: "Selection Required",
        description: "Please select at least 2 roadmaps to merge",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('/api/v1/roadmap/merge/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          roadmap_ids: selectedRoadmaps
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMergePreview(data);
        toast({
          title: "Preview Generated",
          description: "Merge preview is ready for review"
        });
      } else {
        throw new Error('Failed to generate preview');
      }
    } catch (error) {
      toast({
        title: "Preview Failed",
        description: "Could not generate merge preview",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const performMerge = async () => {
    if (!mergePreview) {
      toast({
        title: "Preview Required",
        description: "Please generate a preview first",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('/api/v1/roadmap/merge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          roadmap_ids: selectedRoadmaps,
          schedule_mode: scheduleMode,
          calendar_view: calendarView,
          daily_study_hours: dailyStudyHours
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMergedRoadmap(data.merged_roadmap);
        if (data.merged_roadmap.calendar) {
          setCalendarData(data.merged_roadmap.calendar);
        }
        
        toast({
          title: "Merge Successful!",
          description: `Successfully merged ${data.source_count} roadmaps into your library`
        });
      } else {
        throw new Error('Failed to merge roadmaps');
      }
    } catch (error) {
      toast({
        title: "Merge Failed",
        description: "Could not merge roadmaps",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderCalendarView = () => {
    const sortedDates = Object.keys(calendarData).sort();
    
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">📅 Learning Schedule</h3>
        <div className="grid gap-4">
          {sortedDates.slice(0, 14).map((date) => (
            <Card key={date} className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium">{formatDate(date)}</h4>
                <Badge variant="outline">
                  {formatDuration(
                    calendarData[date].reduce((total, event) => total + event.duration, 0)
                  )}
                </Badge>
              </div>
              <div className="space-y-2">
                {calendarData[date].map((event, index) => (
                  <div key={index} className="flex items-center gap-3 p-2 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2">
                      {event.isCore ? (
                        <Star className="h-4 w-4 text-yellow-500" />
                      ) : (
                        <BookOpen className="h-4 w-4 text-blue-500" />
                      )}
                      <span className="text-sm font-medium">{event.title}</span>
                    </div>
                    <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {event.scheduled_time}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
          <Merge className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Multi-Track Merge</h1>
          <p className="text-muted-foreground">Combine multiple learning paths into one optimized roadmap</p>
        </div>
      </div>

      <Tabs defaultValue="select">
        <TabsList>
          <TabsTrigger value="select">Select & Configure</TabsTrigger>
          {mergePreview ? (
            <TabsTrigger value="preview">Preview & Merge</TabsTrigger>
          ) : (
            <span className="px-4 py-2 rounded-md text-muted-foreground bg-muted cursor-not-allowed select-none">
              Preview & Merge
            </span>
          )}
          {mergedRoadmap ? (
            <TabsTrigger value="result">Result & Timeline</TabsTrigger>
          ) : (
            <span className="px-4 py-2 rounded-md text-muted-foreground bg-muted cursor-not-allowed select-none">
              Result & Timeline
            </span>
          )}
        </TabsList>

        <TabsContent value="select">
          {/* Roadmap Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Select Roadmaps to Merge
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {mergeableRoadmaps.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No roadmaps available for merging</p>
                  <p className="text-sm">Create some roadmaps first to enable merging</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {mergeableRoadmaps.map((roadmap) => (
                    <div
                      key={roadmap.id}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedRoadmaps.includes(roadmap.id)
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                          : 'border-border hover:border-blue-300'
                      }`}
                      onClick={() => 
                        handleRoadmapSelection(
                          roadmap.id, 
                          !selectedRoadmaps.includes(roadmap.id)
                        )
                      }
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold">{roadmap.title}</h3>
                          <p className="text-sm text-muted-foreground">{roadmap.description}</p>
                          <div className="flex items-center gap-4 mt-2">
                            <Badge variant="outline">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatDuration(roadmap.estimatedDuration)}
                            </Badge>
                            <Badge variant="outline">
                              <Users className="h-3 w-3 mr-1" />
                              {roadmap.branchCount} branches
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {selectedRoadmaps.includes(roadmap.id) ? (
                            <CheckCircle className="h-6 w-6 text-blue-500" />
                          ) : (
                            <Plus className="h-6 w-6 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Schedule Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Schedule Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="schedule-mode">Schedule Mode</Label>
                  <Select value={scheduleMode} onValueChange={(value: any) => setScheduleMode(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No Scheduling</SelectItem>
                      <SelectItem value="auto">Auto Schedule (30/60/90 days)</SelectItem>
                      <SelectItem value="manual">Manual Assignment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {scheduleMode === 'auto' && (
                  <div className="space-y-4 p-4 rounded-lg bg-muted/50">
                    <div className="flex items-center space-x-2">
                      <Switch 
                        id="calendar-view" 
                        checked={calendarView}
                        onCheckedChange={setCalendarView}
                      />
                      <Label htmlFor="calendar-view">Generate Calendar Timeline</Label>
                    </div>
                    
                    <div>
                      <Label htmlFor="daily-hours">Daily Study Hours</Label>
                      <Input
                        id="daily-hours"
                        type="number"
                        min="0.5"
                        max="8"
                        step="0.5"
                        value={dailyStudyHours}
                        onChange={(e) => setDailyStudyHours(parseFloat(e.target.value))}
                        className="mt-1"
                      />
                      <p className="text-sm text-muted-foreground mt-1">
                        How many hours per day you plan to study (0.5 - 8.0)
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              <div className="flex gap-3">
                <Button 
                  onClick={generatePreview} 
                  disabled={selectedRoadmaps.length < 2 || isLoading}
                  className="flex-1"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {isLoading ? 'Generating...' : 'Generate Preview'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preview">
          {mergePreview && (
            <>
              {/* Preview Statistics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Merge Statistics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 rounded-lg bg-green-50 dark:bg-green-950/20">
                      <div className="text-2xl font-bold text-green-600">
                        {mergePreview.statistics.efficiency_gain}%
                      </div>
                      <div className="text-sm text-muted-foreground">Efficiency Gain</div>
                    </div>
                    <div className="text-center p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20">
                      <div className="text-2xl font-bold text-blue-600">
                        {formatDuration(mergePreview.statistics.duration_saved)}
                      </div>
                      <div className="text-sm text-muted-foreground">Time Saved</div>
                    </div>
                    <div className="text-center p-4 rounded-lg bg-purple-50 dark:bg-purple-950/20">
                      <div className="text-2xl font-bold text-purple-600">
                        {mergePreview.statistics.final_branches}
                      </div>
                      <div className="text-sm text-muted-foreground">Final Branches</div>
                    </div>
                    <div className="text-center p-4 rounded-lg bg-orange-50 dark:bg-orange-950/20">
                      <div className="text-2xl font-bold text-orange-600">
                        {formatDuration(mergePreview.statistics.final_duration)}
                      </div>
                      <div className="text-sm text-muted-foreground">Total Duration</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Preview Content */}
              <Card>
                <CardHeader>
                  <CardTitle>{mergePreview.preview.title}</CardTitle>
                  <p className="text-muted-foreground">{mergePreview.preview.description}</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <h4 className="font-semibold">Merged Branches ({mergePreview.preview.branches.length})</h4>
                    {mergePreview.preview.branches.map((branch: any, index: number) => (
                      <div key={index} className="p-4 rounded-lg border">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium">{branch.title}</h5>
                          <Badge variant="outline">
                            {formatDuration(branch.estimatedDuration)}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{branch.description}</p>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">
                            {branch.videos?.length || 0} videos
                          </Badge>
                          {branch.videos?.some((v: any) => v.isCore) && (
                            <Badge variant="outline" className="text-yellow-600">
                              <Star className="h-3 w-3 mr-1" />
                              Contains Core Content
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <Separator />

                  <div className="flex justify-center">
                    <Button 
                      onClick={performMerge} 
                      size="lg"
                      disabled={isLoading}
                      className="px-8"
                    >
                      <Shuffle className="h-4 w-4 mr-2" />
                      {isLoading ? 'Merging...' : 'Confirm Merge'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="result">
          {mergedRoadmap && (
            <>
              {/* Success Message */}
              <Card className="border-green-200 bg-green-50 dark:bg-green-950/20">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                    <div>
                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-200">
                        Merge Completed Successfully!
                      </h3>
                      <p className="text-green-700 dark:text-green-300">
                        Your merged roadmap has been saved to your library.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Calendar View */}
              {Object.keys(calendarData).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      Learning Timeline
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderCalendarView()}
                  </CardContent>
                </Card>
              )}

              {/* Next Steps */}
              <Card>
                <CardHeader>
                  <CardTitle>Next Steps</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3">
                    <Button variant="outline" className="justify-start">
                      <BookOpen className="h-4 w-4 mr-2" />
                      View Merged Roadmap
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Start Learning Journey
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Another Merge
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RoadmapMerge;