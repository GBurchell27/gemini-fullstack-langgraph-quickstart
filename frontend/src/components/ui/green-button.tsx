import React from "react";
import { Button, buttonVariants } from "./button";
import { cn } from "@/lib/utils";
import { type VariantProps } from "class-variance-authority";

interface GreenButtonProps extends React.ComponentProps<"button">, 
  VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const GreenButton = React.forwardRef<HTMLButtonElement, GreenButtonProps>(({ 
  className, 
  variant = "outline",
  ...props 
}, ref) => {
  const getGreenStyles = (variant: string) => {
    switch (variant) {
      case "outline":
        return "border-green-500/30 text-green-400 hover:bg-green-600/20 hover:text-green-300 hover:border-green-500/50 bg-transparent";
      case "default":
        return "bg-green-600/20 border border-green-500/30 text-green-400 hover:bg-green-600/30 hover:text-green-300";
      case "ghost":
        return "text-green-400 hover:text-green-300 hover:bg-green-500/10 border-none bg-transparent";
      case "destructive":
        return "text-red-500 hover:text-red-400 hover:bg-red-500/10 border-red-500/30 bg-transparent";
      case "secondary":
        return "bg-green-500/10 text-green-400 hover:bg-green-500/20 hover:text-green-300 border-green-500/20";
      default:
        return "border-green-500/30 text-green-400 hover:bg-green-600/20 hover:text-green-300 hover:border-green-500/50 bg-transparent";
    }
  };

  return (
    <Button
      ref={ref}
      className={cn(
        getGreenStyles(variant || "outline"),
        "transition-all duration-200",
        className
      )}
      variant={variant === "destructive" ? "outline" : variant}
      {...props}
    />
  );
});

GreenButton.displayName = "GreenButton"; 