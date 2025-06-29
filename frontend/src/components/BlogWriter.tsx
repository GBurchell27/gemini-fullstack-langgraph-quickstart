import React, { useState, useEffect, useRef, useCallback } from "react";
import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { BlogWriterForm } from "./BlogWriterForm";
import { BlogWriterProgress, BlogWriterStep } from "./BlogWriterProgress";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  Download, 
  Copy, 
  Eye, 
  Code, 
  RotateCcw, 
  Clock,
  Star,
  TrendingUp,
  SquarePen
} from "lucide-react";

interface BlogResult {
  title: string;
  content: string;
  seo_metadata?: {
    meta_title?: string;
    meta_description?: string;
    focus_keywords?: string[];
    url_slug?: string;
  };
  quality_metrics?: {
    overall_score?: number;
  };
  statistics?: {
    word_count?: number;
    reading_time_minutes?: number;
  };
}

export const BlogWriter: React.FC = () => {
  const [blogSteps, setBlogSteps] = useState<BlogWriterStep[]>([]);
  const [blogResult, setBlogResult] = useState<BlogResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<Date | null>(null);




  const thread = useStream<{
    messages: Message[];
    blog_idea: string;
    target_audience: string;
    writing_tone: string;
    target_length: string;
  }>({
    apiUrl: import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8123",
    assistantId: "blog_writer",
    messagesKey: "messages",
    onUpdateEvent: (event: any) => {
      console.log("🎉 STREAMING EVENT:", Object.keys(event)[0]);
      
      // Extract the first key which contains the node name and data
      const eventKey = Object.keys(event)[0];
      const eventData = event[eventKey];
      
      if (eventData && eventData.current_step) {
        const currentStep = eventData.current_step;
        const progress = eventData.progress || 0;
        
        console.log("📊 PROGRESS UPDATE:", {
          step: currentStep,
          progress: `${Math.round(progress * 100)}%`,
          node: eventKey
        });
        
        // Update blog steps based on current_step from the streaming data
        setBlogSteps(prevSteps => {
          const newSteps = [...prevSteps];
          
          // Find the step that matches the current step
          const currentIndex = newSteps.findIndex(step => 
            step.id === currentStep || 
            step.id.includes(currentStep) ||
            currentStep.includes(step.id)
          );
          
          if (currentIndex >= 0) {
            // Mark previous steps as completed
            for (let i = 0; i < currentIndex; i++) {
              if (newSteps[i].status !== "completed") {
                newSteps[i].status = "completed";
                newSteps[i].timestamp = new Date().toISOString();
              }
            }
            
            // Mark current step as active
            newSteps[currentIndex].status = "active";
            newSteps[currentIndex].timestamp = new Date().toISOString();
            newSteps[currentIndex].details = `Processing ${eventKey}...`;
            
            console.log("✅ STEP UPDATED:", newSteps[currentIndex].title);
          }
          
          return newSteps;
        });
        
        // Check if we have final blog result
        if (eventData.final_blog_result) {
          console.log("🎯 FINAL BLOG RESULT RECEIVED!");
          setBlogResult(eventData.final_blog_result);
          
          // Mark all steps as completed
          setBlogSteps(prevSteps => 
            prevSteps.map(step => ({
              ...step,
              status: "completed" as const,
              timestamp: step.timestamp || new Date().toISOString()
            }))
          );
        }
      }
      
      // Also check for direct final result in other event formats
      if (eventKey === 'final_output_generator' && eventData) {
        console.log("🏁 FINAL OUTPUT DETECTED!");
        
        // Look for blog result in various possible locations
        const finalResult = eventData.final_blog_result || 
                           eventData.blog_result || 
                           eventData.result ||
                           eventData;
                           
        if (finalResult && (finalResult.content || finalResult.markdown_content)) {
          setBlogResult(finalResult);
          
          // Mark all steps as completed with success animation
          setBlogSteps(prevSteps => 
            prevSteps.map(step => ({
              ...step,
              status: "completed" as const,
              timestamp: step.timestamp || new Date().toISOString()
            }))
          );
        }
      }
    },
    onError: (error: unknown) => {
      console.error("Error during blog generation stream:", error);
      setError(error instanceof Error ? error.message : String(error));
    },
  });

  // Initialize default steps
  useEffect(() => {
    const defaultSteps: BlogWriterStep[] = [
      { id: "input_processor", title: "Processing Input", description: "Analyzing blog topic", status: "pending" },
      { id: "topic_analyzer", title: "Topic Analysis", description: "Extracting key topics", status: "pending" },
      { id: "research_coordinator", title: "Research Planning", description: "Creating research strategy", status: "pending" },
      { id: "web_research_dispatcher", title: "Web Research", description: "Gathering online information", status: "pending" },
      { id: "internal_research", title: "Internal Analysis", description: "Finding relevant content", status: "pending" },
      { id: "content_strategist", title: "Content Strategy", description: "Developing content structure", status: "pending" },
      { id: "section_writing_dispatcher", title: "Content Writing", description: "Writing blog sections", status: "pending" },
      { id: "content_assembler", title: "Content Assembly", description: "Assembling final content", status: "pending" },
      { id: "internal_linking", title: "Internal Linking", description: "Adding internal links", status: "pending" },
      { id: "external_linking", title: "External Enhancement", description: "Adding external references", status: "pending" },
      { id: "final_output_generator", title: "Final Output", description: "Generating final blog", status: "pending" }
    ];
    setBlogSteps(defaultSteps);
  }, []);

  const handleBlogSubmit = useCallback((blogData: {
    idea: string;
    targetAudience: string;
    tone: string;
    length: string;
  }) => {
    setError(null);
    setBlogResult(null);
    setStartTime(new Date());
    
    setBlogSteps(prevSteps => 
      prevSteps.map(step => ({ ...step, status: "pending" as const, timestamp: undefined, details: undefined }))
    );

    const newMessages: Message[] = [{
      type: "human",
      content: `Generate a blog post about: ${blogData.idea}`,
      id: Date.now().toString(),
    }];

    const payload = {
      messages: newMessages,
      blog_idea: blogData.idea,
      target_audience: blogData.targetAudience,
      writing_tone: blogData.tone,
      target_length: blogData.length,
    };

    console.log("🚀 SUBMITTING BLOG GENERATION REQUEST");
    thread.submit(payload);
  }, [thread]);

  const handleCancel = useCallback(() => {
    thread.stop();
  }, [thread]);

  const handleReset = useCallback(() => {
    thread.stop();
    setBlogResult(null);
    setError(null);
    setStartTime(null);
    
    setBlogSteps(prevSteps => 
      prevSteps.map(step => ({ ...step, status: "pending" as const, timestamp: undefined, details: undefined }))
    );
  }, [thread]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const downloadAsMarkdown = () => {
    if (!blogResult) return;
    const blob = new Blob([blogResult.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${blogResult.seo_metadata?.url_slug || 'blog-post'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white/90 flex items-center gap-2">
              <SquarePen className="h-6 w-6 text-green-400" />
              AI Blog Writer
            </h1>
            <p className="text-white/60 text-sm">
              Generate SEO-optimized blog posts with AI-powered research and writing
            </p>
          </div>
          {blogResult && (
            <Button
              onClick={handleReset}
              variant="outline"
              size="sm"
              className="border-white/20 text-white/80 hover:bg-white/10"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              New Blog
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        {!blogResult ? (
          // Input and Progress View
          <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
            {/* Left Panel - Form */}
            <div className="bg-white/5 backdrop-blur-lg rounded-lg border border-white/10 p-4">
              <h2 className="text-lg font-semibold text-white/80 mb-4">Create Your Blog Post</h2>
              <BlogWriterForm
                onSubmit={handleBlogSubmit}
                onCancel={handleCancel}
                isLoading={thread.isLoading}
              />
            </div>

            {/* Right Panel - Progress */}
            <div className="bg-white/5 backdrop-blur-lg rounded-lg border border-white/10 p-4">
              <BlogWriterProgress
                steps={blogSteps}
                isLoading={thread.isLoading}
                error={error}
              />
            </div>
          </div>
        ) : (
          // Results View
          <div className="h-full p-4">
            <Tabs defaultValue="content" className="h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <TabsList className="bg-white/10 border border-white/20">
                  <TabsTrigger value="content">
                    <Eye className="h-4 w-4 mr-2" />
                    Preview
                  </TabsTrigger>
                  <TabsTrigger value="markdown">
                    <Code className="h-4 w-4 mr-2" />
                    Markdown
                  </TabsTrigger>
                  <TabsTrigger value="analytics">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Analytics
                  </TabsTrigger>
                </TabsList>
                
                <div className="flex items-center gap-2">
                  <Button
                    onClick={() => copyToClipboard(blogResult.content)}
                    variant="outline"
                    size="sm"
                    className="border-white/20 text-white/80 hover:bg-white/10"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    onClick={downloadAsMarkdown}
                    variant="outline"
                    size="sm"
                    className="border-white/20 text-white/80 hover:bg-white/10"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>

              <div className="flex-1 overflow-hidden">
                <TabsContent value="content" className="h-full">
                  <Card className="h-full bg-white/5 border-white/10">
                    <ScrollArea className="h-full p-6">
                      <div className="prose prose-invert max-w-none text-white/80">
                        <pre className="whitespace-pre-wrap font-sans">{blogResult.content}</pre>
                      </div>
                    </ScrollArea>
                  </Card>
                </TabsContent>

                <TabsContent value="markdown" className="h-full">
                  <Card className="h-full bg-white/5 border-white/10">
                    <ScrollArea className="h-full p-6">
                      <pre className="text-white/80 text-sm font-mono whitespace-pre-wrap">
                        {blogResult.content}
                      </pre>
                    </ScrollArea>
                  </Card>
                </TabsContent>

                <TabsContent value="analytics" className="h-full">
                  <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <Card className="bg-white/5 border-white/10 p-4">
                      <h3 className="text-lg font-semibold text-white/80 mb-4">SEO Optimization</h3>
                      <div className="space-y-3">
                        {blogResult.seo_metadata?.meta_title && (
                          <div>
                            <label className="text-xs text-white/60">Meta Title</label>
                            <p className="text-white/80 text-sm">{blogResult.seo_metadata.meta_title}</p>
                          </div>
                        )}
                        {blogResult.seo_metadata?.meta_description && (
                          <div>
                            <label className="text-xs text-white/60">Meta Description</label>
                            <p className="text-white/80 text-sm">{blogResult.seo_metadata.meta_description}</p>
                          </div>
                        )}
                        {blogResult.seo_metadata?.focus_keywords && (
                          <div>
                            <label className="text-xs text-white/60">Focus Keywords</label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {blogResult.seo_metadata.focus_keywords.map((keyword, index) => (
                                <Badge key={index} className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </Card>

                    <Card className="bg-white/5 border-white/10 p-4">
                      <h3 className="text-lg font-semibold text-white/80 mb-4">Quality Analysis</h3>
                      <div className="space-y-3">
                        {blogResult.quality_metrics?.overall_score && (
                          <div className="flex items-center justify-between">
                            <span className="text-white/70">Overall Score</span>
                            <div className="flex items-center gap-2">
                              <Star className="h-4 w-4 text-yellow-400" />
                              <span className="text-white/90 font-semibold">
                                {Math.round(blogResult.quality_metrics.overall_score * 10)}/10
                              </span>
                            </div>
                          </div>
                        )}
                        {blogResult.statistics?.word_count && (
                          <div className="flex items-center justify-between">
                            <span className="text-white/70">Word Count</span>
                            <span className="text-white/90">{blogResult.statistics.word_count}</span>
                          </div>
                        )}
                        {blogResult.statistics?.reading_time_minutes && (
                          <div className="flex items-center justify-between">
                            <span className="text-white/70">Reading Time</span>
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4 text-white/60" />
                              <span className="text-white/90">{blogResult.statistics.reading_time_minutes} min</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </Card>
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}; 