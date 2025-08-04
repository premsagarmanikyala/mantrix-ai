import React from "react";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>((props, ref) => {
  return (
    <input
      ref={ref}
      {...props}
      className="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
});
Input.displayName = "Input";
