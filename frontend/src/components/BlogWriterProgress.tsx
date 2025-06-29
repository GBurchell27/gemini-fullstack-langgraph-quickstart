import React, { useEffect, useState } from "react";
import { CheckCircle, Circle, Loader2, Clock, AlertCircle, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

export interface BlogWriterStep {
  id: string;
  title: string;
  description: string;
  status: "pending" | "active" | "completed" | "error";
  timestamp?: string;
  details?: string;
  duration?: number;
}

interface BlogWriterProgressProps {
  steps: BlogWriterStep[];
  isLoading: boolean;
  error?: string | null;
}

const defaultSteps: BlogWriterStep[] = [
  {
    id: "input_processing",
    title: "Processing Input",
    description: "Analyzing blog topic and requirements",
    status: "pending"
  },
  {
    id: "topic_analysis",
    title: "Topic Analysis",
    description: "Extracting key topics and generating research questions",
    status: "pending"
  },
  {
    id: "research_coordination",
    title: "Research Planning",
    description: "Creating research strategy and resource allocation",
    status: "pending"
  },
  {
    id: "web_research",
    title: "Web Research",
    description: "Gathering information from online sources",
    status: "pending"
  },
  {
    id: "internal_research",
    title: "Internal Content Analysis",
    description: "Finding relevant internal content and linking opportunities",
    status: "pending"
  },
  {
    id: "content_strategist",
    title: "Content Strategy",
    description: "Developing content structure and strategy",
    status: "pending"
  },
  {
    id: "section_writing",
    title: "Content Writing",
    description: "Writing blog sections with research integration",
    status: "pending"
  },
  {
    id: "content_assembler",
    title: "Content Assembly",
    description: "Assembling sections with transitions and formatting",
    status: "pending"
  },
  {
    id: "internal_linking",
    title: "Internal Linking",
    description: "Adding contextual internal links",
    status: "pending"
  },
  {
    id: "external_linking",
    title: "External Enhancement",
    description: "Validating and adding external references",
    status: "pending"
  },
  {
    id: "final_output",
    title: "Final Output",
    description: "Generating final blog with SEO optimization",
    status: "pending"
  }
];

export const BlogWriterProgress: React.FC<BlogWriterProgressProps> = ({
  steps = defaultSteps,
  isLoading,
  error
}) => {
  const [recentlyCompleted, setRecentlyCompleted] = useState<Set<string>>(new Set());

  // Track recently completed steps for special animations
  useEffect(() => {
    const newlyCompleted = steps
      .filter(step => step.status === "completed")
      .map(step => step.id)
      .filter(id => !recentlyCompleted.has(id));

    if (newlyCompleted.length > 0) {
      setRecentlyCompleted(prev => new Set([...prev, ...newlyCompleted]));
      
      // Remove from recently completed after animation duration
      const timer = setTimeout(() => {
        setRecentlyCompleted(prev => {
          const updated = new Set(prev);
          newlyCompleted.forEach(id => updated.delete(id));
          return updated;
        });
      }, 2000); // 2 second celebration animation

      return () => clearTimeout(timer);
    }
  }, [steps, recentlyCompleted]);
  const getStepIcon = (step: BlogWriterStep) => {
    const isRecentlyCompleted = recentlyCompleted.has(step.id);
    
    switch (step.status) {
      case "completed":
        return (
          <div className="relative">
            <CheckCircle 
              className={`h-5 w-5 text-green-400 ${
                isRecentlyCompleted 
                  ? "animate-bounce" 
                  : "animate-pulse"
              }`} 
            />
            <Sparkles 
              className={`h-3 w-3 text-green-300 absolute -top-1 -right-1 ${
                isRecentlyCompleted 
                  ? "animate-ping" 
                  : "animate-pulse"
              }`} 
            />
            {isRecentlyCompleted && (
              <div className="absolute inset-0 h-5 w-5 rounded-full bg-green-400/30 animate-ping" />
            )}
          </div>
        );
      case "active":
        return (
          <div className="relative">
            <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
            <div className="absolute inset-0 h-5 w-5 rounded-full bg-blue-400/20 animate-ping" />
          </div>
        );
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-400 animate-bounce" />;
      default:
        return <Circle className="h-5 w-5 text-white/30 animate-pulse opacity-50" />;
    }
  };

  const getStepBadge = (step: BlogWriterStep) => {
    const isRecentlyCompleted = recentlyCompleted.has(step.id);
    
    switch (step.status) {
      case "completed":
        return (
          <Badge className={`bg-green-500/20 text-green-400 border-green-500/30 ${
            isRecentlyCompleted ? "animate-pulse shadow-lg shadow-green-500/30" : ""
          }`}>
            ✨ Completed
          </Badge>
        );
      case "active":
        return (
          <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse">
            🔄 In Progress
          </Badge>
        );
      case "error":
        return (
          <Badge className="bg-red-500/20 text-red-400 border-red-500/30 animate-bounce">
            ❌ Error
          </Badge>
        );
      default:
        return (
          <Badge className="bg-white/5 text-white/40 border-white/10">
            ⏳ Waiting
          </Badge>
        );
    }
  };

  const completedSteps = steps.filter(step => step.status === "completed").length;
  const totalSteps = steps.length;
  const progressPercentage = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  const formatDuration = (duration?: number) => {
    if (!duration) return "";
    if (duration < 60) return `${Math.round(duration)}s`;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.round(duration % 60);
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="h-full flex flex-col min-h-0">
      {/* Header */}
      <div className="flex-shrink-0 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-white/80">Blog Generation Progress</h2>
          <div className="text-sm text-white/60">
            {completedSteps}/{totalSteps} steps
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-white/10 rounded-full h-2 mb-2 relative overflow-hidden">
          <div 
            className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500 ease-out relative"
            style={{ width: `${progressPercentage}%` }}
          >
            {/* Animated shine effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
          </div>
          {/* Completion celebration effect */}
          {progressPercentage === 100 && (
            <div className="absolute inset-0 bg-gradient-to-r from-green-400/30 to-emerald-400/30 rounded-full animate-ping" />
          )}
        </div>
        
        <div className="text-xs text-white/50">
          {isLoading ? "Generating your blog post..." : "Ready"}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex-shrink-0 mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Error occurred</span>
          </div>
          <ScrollArea className="h-24 mt-2">
            <div className="text-red-300/80 text-xs pr-3">{error}</div>
          </ScrollArea>
        </div>
      )}

      {/* Steps List - Takes remaining space */}
      <div className="flex-1 flex flex-col min-h-0">
        <ScrollArea className="flex-1 max-h-[400px]">
          <div className="space-y-3 pr-4">
            {steps.map((step, index) => {
              const isRecentlyCompleted = recentlyCompleted.has(step.id);
              
              return (
                <div
                  key={step.id}
                  className={`p-3 rounded-lg border transition-all duration-300 ${
                    step.status === "active"
                      ? "bg-blue-500/10 border-blue-500/30 shadow-lg shadow-blue-500/20 animate-pulse"
                      : step.status === "completed"
                      ? `bg-green-500/10 border-green-500/30 shadow-lg shadow-green-500/20 ${
                          isRecentlyCompleted ? "animate-pulse border-green-400/50" : ""
                        }`
                      : step.status === "error"
                      ? "bg-red-500/10 border-red-500/30 shadow-lg shadow-red-500/20 animate-pulse"
                      : "bg-white/5 border-white/10 hover:bg-white/10"
                  }`}
                >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="mt-0.5">
                      {getStepIcon(step)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-medium text-white/90 truncate">
                          {step.title}
                        </h3>
                        {getStepBadge(step)}
                      </div>
                      <p className="text-xs text-white/60 leading-relaxed">
                        {step.description}
                      </p>
                      {step.details && (
                        <p className="text-xs text-white/50 mt-1 italic">
                          {step.details}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Timestamp and Duration */}
                  <div className="flex flex-col items-end gap-1 text-xs text-white/40">
                    {step.timestamp && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(step.timestamp).toLocaleTimeString()}
                      </div>
                    )}
                    {step.duration && (
                      <div className="text-white/50">
                        {formatDuration(step.duration)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              );
            })}
          </div>
        </ScrollArea>
        
        {/* Summary Stats - Fixed at bottom */}
        {completedSteps > 0 && (
          <div className="flex-shrink-0 mt-4 pt-4 border-t border-white/10">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-green-400">
                  {completedSteps}
                </div>
                <div className="text-xs text-white/50">Completed</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-blue-400">
                  {steps.filter(s => s.status === "active").length}
                </div>
                <div className="text-xs text-white/50">Active</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-white/60">
                  {steps.filter(s => s.status === "pending").length}
                </div>
                <div className="text-xs text-white/50">Pending</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 