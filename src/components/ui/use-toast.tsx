import * as React from "react";
import { toast as sonnerToast, Toaster as SonnerToaster } from "sonner";

type ToastProps = React.ComponentProps<typeof SonnerToaster>;

const Toaster = ({ ...props }: ToastProps) => {
  return (
    <SonnerToaster
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-white group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-gray-500",
          actionButton:
            "group-[.toast]:bg-blue-600 group-[.toast]:text-white",
          cancelButton:
            "group-[.toast]:bg-gray-200 group-[.toast]:text-gray-600",
          error:
            "group-[.toaster]:border-red-500 group-[.toaster]:bg-red-50",
          success:
            "group-[.toaster]:border-green-500 group-[.toaster]:bg-green-50",
          warning:
            "group-[.toaster]:border-yellow-500 group-[.toaster]:bg-yellow-50",
          info:
            "group-[.toaster]:border-blue-500 group-[.toaster]:bg-blue-50",
        },
      }}
      {...props}
    />
  );
};

export { Toaster, sonnerToast as toast }; 