import { useState } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Brain, Send, StopCircle, Zap, Cpu } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string, model: string) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");
  const [effort, setEffort] = useState("medium");
  const [model, setModel] = useState("gemini-2.5-flash-preview-04-17");

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort, model);
    setInternalInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (
    <form
      onSubmit={handleInternalSubmit}
      className={`flex flex-col gap-3 p-3 pb-4`}
    >
      <div
        className={`flex flex-row items-center justify-between text-white rounded-2xl break-words min-h-7 bg-white/5 backdrop-blur-lg border border-white/10 px-4 pt-3`}
      >
        <Textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Who won the Euro 2024 and scored the most goals?"
          className={`w-full text-white/80 placeholder-white/40 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none bg-transparent
                        md:text-base  min-h-[56px] max-h-[200px]`}
          rows={1}
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
                  : "text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
              } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
              disabled={isSubmitDisabled}
            >
              <Send className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex flex-row gap-2">
          <div className="flex flex-row gap-2 bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 focus:ring-neutral-500 rounded-lg pl-2 pr-2 max-w-[100%] sm:max-w-[90%]">
            <div className="flex flex-row items-center text-sm">
              <Brain className="h-4 w-4 mr-2" />
              Effort
            </div>
            <Select value={effort} onValueChange={setEffort}>
              <SelectTrigger className="w-[120px] bg-transparent border-none cursor-pointer text-white/90">
                <SelectValue placeholder="Effort" />
              </SelectTrigger>
              <SelectContent className="bg-black/50 backdrop-blur-xl border-white/10 text-white/80 cursor-pointer">
                <SelectItem
                  value="low"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  Low
                </SelectItem>
                <SelectItem
                  value="medium"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  Medium
                </SelectItem>
                <SelectItem
                  value="high"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  High
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-row gap-2 bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 focus:ring-neutral-500 rounded-lg pl-2 pr-2 max-w-[100%] sm:max-w-[90%]">
            <div className="flex flex-row items-center text-sm ml-2">
              <Cpu className="h-4 w-4 mr-2" />
              Model
            </div>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger className="w-[150px] bg-transparent border-none cursor-pointer text-white/90">
                <SelectValue placeholder="Model" />
              </SelectTrigger>
              <SelectContent className="bg-black/50 backdrop-blur-xl border-white/10 text-white/80 cursor-pointer">
                <SelectItem
                  value="gemini-2.0-flash"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-yellow-400" /> 2.0 Flash
                  </div>
                </SelectItem>
                <SelectItem
                  value="gemini-2.5-flash-preview-04-17"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-orange-400" /> 2.5 Flash
                  </div>
                </SelectItem>
                <SelectItem
                  value="gemini-2.5-pro-preview-05-06"
                  className="hover:bg-white/10 focus:bg-white/10 cursor-pointer"
                >
                  <div className="flex items-center">
                    <Cpu className="h-4 w-4 mr-2 text-purple-400" /> 2.5 Pro
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        {hasHistory && (
          <Button
            className="bg-white/5 backdrop-blur-lg border border-white/10 text-white/70 cursor-pointer rounded-lg pl-2 pr-4"
            variant="default"
            onClick={() => window.location.reload()}
          >
            <SquarePen size={16} className="mr-2" />
            New Search
          </Button>
        )}
      </div>
    </form>
  );
};
