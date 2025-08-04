import { useCallback } from "react";
import { toast, Toaster } from "react-hot-toast";

export function useToast() {
  const showToast = useCallback((message: string, type: "success" | "error" = "success") => {
    if (type === "success") {
      toast.success(message);
    } else {
      toast.error(message);
    }
  }, []);

  return { showToast, Toaster };
}
