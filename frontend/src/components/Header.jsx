import React, { useState } from 'react';
import { Layers, Key, Home, Settings as SettingsIcon, FileSpreadsheet } from 'lucide-react';
import ApiKeyModal from './ApiKeyModal';

export default function Header({ currentProject, onGoHome, onOpenSettings, onOpenExport }) {
  const [showKeyModal, setShowKeyModal] = useState(false);

  return (
    <header className="header">
      <div className="logo-area" onClick={onGoHome}>
        <div className="logo-icon">SR</div>
        <div>
          <span className="logo-title">SiteReportX</span>
          <span className="logo-badge" style={{ marginLeft: '8px' }}>배관내시경</span>
        </div>
      </div>

      <div className="header-actions">
        {currentProject && (
          <>
            <button className="btn btn-secondary" onClick={onGoHome}>
              <Home size={15} /> 현장 목록
            </button>
            <button className="btn btn-secondary" onClick={onOpenSettings}>
              <SettingsIcon size={15} /> 현장 설정
            </button>
            <button className="btn btn-success" onClick={onOpenExport}>
              <FileSpreadsheet size={15} /> 보고서 출력
            </button>
          </>
        )}
        <button className="btn btn-secondary" onClick={() => setShowKeyModal(true)}>
          <Key size={15} /> API 키
        </button>
      </div>

      <ApiKeyModal isOpen={showKeyModal} onClose={() => setShowKeyModal(false)} />
    </header>
  );
}
