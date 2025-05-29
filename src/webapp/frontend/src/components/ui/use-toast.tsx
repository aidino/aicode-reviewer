import * as React from "react";
import { Toaster as Sonner } from "sonner";

type ToastProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToastProps) => {
  return (
    <Sonner
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-white group-[.toaster]:border-border group-[.toaster]:shadow-lg dark:group-[.toaster]:bg-zinc-950 dark:group-[.toaster]:border-zinc-800",
          description: "group-[.toast]:text-muted-foreground",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
          error:
            "group-[.toaster]:border-red-500 group-[.toaster]:bg-red-50 dark:group-[.toaster]:border-red-900 dark:group-[.toaster]:bg-red-950",
          success:
            "group-[.toaster]:border-green-500 group-[.toaster]:bg-green-50 dark:group-[.toaster]:border-green-900 dark:group-[.toaster]:bg-green-950",
          warning:
            "group-[.toaster]:border-yellow-500 group-[.toaster]:bg-yellow-50 dark:group-[.toaster]:border-yellow-900 dark:group-[.toaster]:bg-yellow-950",
          info:
            "group-[.toaster]:border-blue-500 group-[.toaster]:bg-blue-50 dark:group-[.toaster]:border-blue-900 dark:group-[.toaster]:bg-blue-950",
          // Add custom styling for different types of toasts here
        },
      }}
      {...props}
    />
  );
};

import { toast } from "sonner";

export { Toaster, toast }; 