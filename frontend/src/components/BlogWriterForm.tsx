import { useState } from "react";
import { Button } from "@/components/ui/button";
import { PenLine, User, Palette, Hash, Send, StopCircle } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface BlogWriterFormProps {
  onSubmit: (blogData: {
    idea: string;
    targetAudience: string;
    tone: string;
    length: string;
  }) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export const BlogWriterForm: React.FC<BlogWriterFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [idea, setIdea] = useState("");
  const [targetAudience, setTargetAudience] = useState("general");
  const [tone, setTone] = useState("professional");
  const [length, setLength] = useState("medium");

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!idea.trim()) return;
    
    onSubmit({
      idea: idea.trim(),
      targetAudience,
      tone,
      length
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isSubmitDisabled = !idea.trim() || isLoading;

  const blogIdeaExamples = [
    "How to conduct systematic reviews in healthcare",
    "Best practices for remote team management",
    "Getting started with React and TypeScript",
    "The future of artificial intelligence in education",
    "Sustainable living tips for busy professionals"
  ];

  const randomPlaceholder = blogIdeaExamples[Math.floor(Math.random() * blogIdeaExamples.length)];

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-4"
    >
      {/* Blog Idea Input */}
      <div className="flex flex-col gap-2">
        <label className="text-white/70 text-sm font-medium flex items-center gap-2">
          <PenLine className="h-4 w-4" />
          Blog Topic or Idea
        </label>
        <div className="flex flex-row items-center justify-between text-white rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10 px-4 pt-3">
          <Textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={randomPlaceholder}
            className="w-full text-white/80 placeholder-white/40 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none bg-transparent md:text-base min-h-[60px] max-h-[120px]"
            rows={2}
          />
          <div className="-mt-3">
            {isLoading ? (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200"
                onClick={onCancel}
              >
                <StopCircle className="h-5 w-5" />
              </Button>
            ) : (
              <Button
                type="submit"
                variant="ghost"
                className={`${
                  isSubmitDisabled
                    ? "text-white/30"
                    : "text-green-400 hover:text-green-300 hover:bg-green-500/10"
                } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
                disabled={isSubmitDisabled}
              >
                <Send className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Target Audience */}
        <div className="flex flex-col gap-2">
          <label className="text-white/70 text-sm font-medium flex items-center gap-2">
            <User className="h-4 w-4" />
            Target Audience
          </label>
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 rounded-lg">
            <Select value={targetAudience} onValueChange={setTargetAudience}>
              <SelectTrigger className="bg-transparent border-none cursor-pointer text-white/90">
                <SelectValue placeholder="Select audience" />
              </SelectTrigger>
              <SelectContent className="bg-black/50 backdrop-blur-xl border-white/10 text-white/80">
                <SelectItem value="general" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  General Audience
                </SelectItem>
                <SelectItem value="professionals" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Professionals
                </SelectItem>
                <SelectItem value="students" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Students
                </SelectItem>
                <SelectItem value="researchers" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Researchers
                </SelectItem>
                <SelectItem value="beginners" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Beginners
                </SelectItem>
                <SelectItem value="experts" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Experts
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Writing Tone */}
        <div className="flex flex-col gap-2">
          <label className="text-white/70 text-sm font-medium flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Writing Tone
          </label>
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 rounded-lg">
            <Select value={tone} onValueChange={setTone}>
              <SelectTrigger className="bg-transparent border-none cursor-pointer text-white/90">
                <SelectValue placeholder="Select tone" />
              </SelectTrigger>
              <SelectContent className="bg-black/50 backdrop-blur-xl border-white/10 text-white/80">
                <SelectItem value="professional" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Professional
                </SelectItem>
                <SelectItem value="casual" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Casual
                </SelectItem>
                <SelectItem value="technical" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Technical
                </SelectItem>
                <SelectItem value="conversational" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Conversational
                </SelectItem>
                <SelectItem value="academic" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Academic
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Blog Length */}
        <div className="flex flex-col gap-2">
          <label className="text-white/70 text-sm font-medium flex items-center gap-2">
            <Hash className="h-4 w-4" />
            Blog Length
          </label>
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 rounded-lg">
            <Select value={length} onValueChange={setLength}>
              <SelectTrigger className="bg-transparent border-none cursor-pointer text-white/90">
                <SelectValue placeholder="Select length" />
              </SelectTrigger>
              <SelectContent className="bg-black/50 backdrop-blur-xl border-white/10 text-white/80">
                <SelectItem value="short" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Short (500-800 words)
                </SelectItem>
                <SelectItem value="medium" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Medium (1000-1500 words)
                </SelectItem>
                <SelectItem value="long" className="hover:bg-white/10 focus:bg-white/10 cursor-pointer">
                  Long (2000+ words)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between mt-2">
        <div className="text-xs text-white/40">
          Use Ctrl+Enter to submit • AI-powered content generation with SEO optimization
        </div>
        {!isLoading && (
          <Button
            type="submit"
            disabled={isSubmitDisabled}
            className="bg-green-600/20 border border-green-500/30 text-green-400 hover:bg-green-600/30 hover:text-green-300 transition-all duration-200"
          >
            <PenLine className="h-4 w-4 mr-2" />
            Generate Blog
          </Button>
        )}
      </div>
    </form>
  );
}; 