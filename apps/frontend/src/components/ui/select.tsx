import * as React from "react";
import { cn } from "@/lib/utils";

export const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, ...props }, ref) => {
  return (
    <select
      className={cn(
        "block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Select.displayName = "Select";

export const SelectTrigger = ({
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button
    className="inline-flex items-center justify-between w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm"
    {...props}
  >
    {children}
  </button>
);

export const SelectValue = ({ children }: { children: React.ReactNode }) => (
  <span>{children}</span>
);

export const SelectContent = ({
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div className="absolute mt-1 w-full rounded-md bg-white shadow-lg z-10" {...props}>
    {children}
  </div>
);

export const SelectItem = ({
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className="cursor-pointer px-4 py-2 text-sm hover:bg-gray-100"
    {...props}
  >
    {children}
  </div>
);
