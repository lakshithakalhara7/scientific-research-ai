import { useState } from "react";
import Sidebar from "./Sidebar";
import "./DashboardLayout.css";

function DashboardLayout({
  children,
  activePage,
  onNewResearch,
  onPaperAnalyzer,
  onSourceVerification,
  onResearchInsights,
  onAIAssistant,
}) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div
      className={`research-app-shell ${
        sidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((previous) => !previous)}
        activePage={activePage}
        onNewResearch={onNewResearch}
        onPaperAnalyzer={onPaperAnalyzer}
        onSourceVerification={onSourceVerification}
        onResearchInsights={onResearchInsights}
        onAIAssistant={onAIAssistant}
      />

      <div className="research-workspace">{children}</div>
    </div>
  );
}

export default DashboardLayout;
