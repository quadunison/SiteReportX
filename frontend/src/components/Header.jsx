import React, { useState } from 'react';
import { Layers, Key, ChevronLeft, Settings as SettingsIcon, Download, ShieldCheck } from 'lucide-react';
import ApiKeyModal from './ApiKeyModal';

export default function Header({ currentProject, onGoHome, onOpenSettings, onOpenExport }) {
  const [showKeyModal, setShowKeyModal] = useState(false);

  return (
    <header className="header">
      <div className="logo-area" onClick={onGoHome} title="홈으로 이동">
        <div className="logo-icon">
          <Layers size={18} strokeWidth={2.4} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="logo-title">SiteReportX</span>
          <span className="logo-badge">Industrial Pro</span>
        </div>
      </div>

      <div className="header-actions">
        {currentProject && (
          <>
            <button className="btn btn-secondary" onClick={onGoHome}>
              <ChevronLeft size={15} /> 현장 목록
            </button>
            <button className="btn btn-secondary" onClick={onOpenSettings}>
              <SettingsIcon size={15} /> 현장 설정
            </button>
            <button className="btn btn-primary" onClick={onOpenExport}>
              <Download size={15} /> 보고서 출력
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
