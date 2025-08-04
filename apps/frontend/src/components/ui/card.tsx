import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-2xl border bg-white p-4 shadow-sm dark:bg-gray-900 dark:border-gray-700",
      className,
    )}
    {...props}
  />
));
Card.displayName = "Card";

const CardHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("mb-2", className)} {...props} />
);
CardHeader.displayName = "CardHeader";

const CardTitle = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3
    className={cn(
      "text-lg font-semibold leading-tight tracking-tight",
      className,
    )}
    {...props}
  />
);
CardTitle.displayName = "CardTitle";

const CardContent = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("text-sm text-gray-700 dark:text-gray-300", className)}
    {...props}
  />
);
CardContent.displayName = "CardContent";

export { Card, CardHeader, CardTitle, CardContent };
