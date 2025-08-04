import React, { useState, ReactNode } from "react";

type TabsProps = {
  children: ReactNode;
  defaultValue?: string;
};

export const Tabs = ({ children, defaultValue }: TabsProps) => {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <div>
      {React.Children.map(children, (child) =>
        React.isValidElement(child)
          ? React.cloneElement(child, { activeTab, setActiveTab })
          : child,
      )}
    </div>
  );
};

type TabsListProps = {
  children: ReactNode;
  activeTab?: string;
  setActiveTab?: (value: string) => void;
};

export const TabsList = ({
  children,
  activeTab,
  setActiveTab,
}: TabsListProps) => {
  return (
    <div className="flex border-b">
      {React.Children.map(children, (child) =>
        React.isValidElement(child)
          ? React.cloneElement(child, { activeTab, setActiveTab })
          : child,
      )}
    </div>
  );
};

type TabsTriggerProps = {
  value: string;
  children: ReactNode;
  activeTab?: string;
  setActiveTab?: (value: string) => void;
};

export const TabsTrigger = ({
  value,
  children,
  activeTab,
  setActiveTab,
}: TabsTriggerProps) => {
  const isActive = activeTab === value;
  return (
    <button
      className={`px-4 py-2 ${
        isActive ? "border-b-2 border-blue-500 font-semibold" : ""
      }`}
      onClick={() => setActiveTab && setActiveTab(value)}
    >
      {children}
    </button>
  );
};

type TabsContentProps = {
  value: string;
  children: ReactNode;
  activeTab?: string;
};

export const TabsContent = ({
  value,
  children,
  activeTab,
}: TabsContentProps) => {
  if (activeTab !== value) return null;
  return <div className="p-4">{children}</div>;
};
