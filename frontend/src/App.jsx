import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ProjectDashboard from './components/ProjectDashboard';
import InspectionWorkspace from './components/InspectionWorkspace';
import ProjectSettingsModal from './components/ProjectSettingsModal';
import ReportModal from './components/ReportModal';

export default function App() {
  const [currentProjectId, setCurrentProjectId] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);

  const fetchCurrentProject = async (id) => {
    if (!id) return;
    try {
      const res = await fetch(`/api/projects/${id}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentProject(data);
      }
    } catch (err) {
      console.error('현장 로드 실패:', err);
    }
  };

  useEffect(() => {
    if (currentProjectId) {
      fetchCurrentProject(currentProjectId);
    } else {
      setCurrentProject(null);
    }
  }, [currentProjectId]);

  return (
    <div className="app-container">
      <Header 
        currentProject={currentProject}
        onGoHome={() => setCurrentProjectId(null)}
        onOpenSettings={() => setShowSettingsModal(true)}
        onOpenExport={() => setShowExportModal(true)}
      />

      <main className="main-content">
        {!currentProjectId ? (
          <ProjectDashboard 
            onSelectProject={(id) => setCurrentProjectId(id)} 
          />
        ) : currentProject ? (
          <InspectionWorkspace 
            project={currentProject} 
            onProjectUpdated={() => fetchCurrentProject(currentProjectId)} 
            onOpenReportModal={() => setShowExportModal(true)}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
            현장 데이터를 불러오는 중...
          </div>
        )}
      </main>

      {/* 설정 모달 */}
      <ProjectSettingsModal 
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
        project={currentProject}
        onSettingsUpdated={() => fetchCurrentProject(currentProjectId)}
      />

      {/* 보고서 출력 모달 */}
      <ReportModal 
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        project={currentProject}
      />
    </div>
  );
}
