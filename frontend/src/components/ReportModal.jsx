import React, { useState } from 'react';
import { FileSpreadsheet, Archive, Download, X, CheckCircle, Loader } from 'lucide-react';

export default function ReportModal({ isOpen, onClose, project }) {
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);

  if (!isOpen || !project) return null;

  const handleGenerate = async () => {
    setGenerating(true);
    setResult(null);
    try {
      const res = await fetch(`/api/projects/${project.id}/generate-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
      } else {
        alert('보고서 생성 실패: ' + data.detail);
      }
    } catch (err) {
      alert('오류 발생: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileSpreadsheet size={20} color="#10B981" />
            <h3 className="modal-title">보고서 출력 및 파일 내보내기</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '4px' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '20px' }}>
          <div style={{ fontWeight: 700, fontSize: '15px', marginBottom: '4px' }}>{project.name}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            총 검사 항목: {project.items?.length || 0}건 | 이상 배관: {project.items?.filter(i => i.defect !== '정상' && i.defect !== '').length || 0}건
          </div>
        </div>

        {!result && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <button className="btn btn-primary" onClick={handleGenerate} disabled={generating} style={{ padding: '12px 24px', fontSize: '14px' }}>
              {generating ? (
                <><Loader size={18} className="animate-spin" /> 보고서 생성 중...</>
              ) : (
                <><FileSpreadsheet size={18} /> 원클릭 엑셀 보고서 & ZIP 생성하기</>
              )}
            </button>
          </div>
        )}

        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', fontWeight: 600, fontSize: '14px', marginBottom: '8px' }}>
              <CheckCircle size={18} /> 산출물 생성이 완료되었습니다!
            </div>

            <a 
              href={result.excel_download_url} 
              download 
              className="btn btn-success" 
              style={{ justifyContent: 'center', padding: '12px' }}
            >
              <FileSpreadsheet size={18} /> 실무 엑셀 보고서 다운로드 (.xlsx)
            </a>

            <a 
              href={result.zip_download_url} 
              download 
              className="btn btn-primary" 
              style={{ justifyContent: 'center', padding: '12px' }}
            >
              <Archive size={18} /> 표준 파일명 미디어 압축팩 다운로드 (.zip)
            </a>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <button className="btn btn-secondary" onClick={onClose}>닫기</button>
        </div>
      </div>
    </div>
  );
}
