import React from "react";
import { Badge, badgeVariants } from "./badge";
import { cn } from "@/lib/utils";
import { type VariantProps } from "class-variance-authority";

interface GreenBadgeProps extends React.ComponentProps<"span">,
  VariantProps<typeof badgeVariants> {
  asChild?: boolean;
}

export const GreenBadge = React.forwardRef<HTMLSpanElement, GreenBadgeProps>(
  ({ className, ...props }, ref) => {
    return (
      <Badge
        ref={ref}
        className={cn(
          "bg-green-500/20 text-green-400 border-green-500/30 hover:bg-green-500/30 transition-colors",
          className
        )}
        {...props}
      />
    );
  }
);

GreenBadge.displayName = "GreenBadge"; 