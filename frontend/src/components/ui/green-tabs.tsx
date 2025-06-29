import React from "react";
import { TabsList, TabsTrigger } from "./tabs";
import { cn } from "@/lib/utils";

interface GreenTabsListProps extends React.ComponentProps<typeof TabsList> {}

interface GreenTabsTriggerProps extends React.ComponentProps<typeof TabsTrigger> {}

export const GreenTabsList = React.forwardRef<
  React.ElementRef<typeof TabsList>,
  GreenTabsListProps
>(({ className, ...props }, ref) => (
  <TabsList
    ref={ref}
    className={cn(
      "bg-green-500/10 border border-green-500/20 data-[state=active]:bg-green-500/20",
      className
    )}
    {...props}
  />
));

export const GreenTabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsTrigger>,
  GreenTabsTriggerProps
>(({ className, ...props }, ref) => (
  <TabsTrigger
    ref={ref}
    className={cn(
      "text-white/70 data-[state=active]:text-green-400 data-[state=active]:bg-green-500/20 hover:text-green-300 hover:bg-green-500/10",
      className
    )}
    {...props}
  />
));

GreenTabsList.displayName = "GreenTabsList";
GreenTabsTrigger.displayName = "GreenTabsTrigger"; 