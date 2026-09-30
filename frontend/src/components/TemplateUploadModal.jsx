import React, { useState, useEffect, useRef } from 'react';
import { X, UploadCloud, FileSpreadsheet, RotateCcw, CheckCircle2, Download, AlertCircle } from 'lucide-react';

export default function TemplateUploadModal({ isOpen, onClose, projectId, onTemplateChanged }) {
  const [templateInfo, setTemplateInfo] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const fetchTemplateInfo = async () => {
    try {
      const res = await fetch(`/api/projects/${projectId}/template/info`);
      const data = await res.json();
      setTemplateInfo(data);
    } catch (err) {
      console.error('템플릿 정보 조회 실패:', err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTemplateInfo();
    }
  }, [isOpen, projectId]);

  if (!isOpen) return null;

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xlsm')) {
      alert('엑셀 파일(.xlsx, .xlsm)만 업로드 가능합니다.');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`/api/projects/${projectId}/template`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        alert('마스터 엑셀 서식 템플릿이 성공적으로 등록되었습니다.');
        fetchTemplateInfo();
        onTemplateChanged?.();
      } else {
        const err = await res.json();
        alert('업로드 실패: ' + (err.detail || '오류 발생'));
      }
    } catch (err) {
      alert('업로드 오류: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('기본 마스터 템플릿(master_sample_0416.xlsx)으로 복원하시겠습니까?')) return;
    try {
      await fetch(`/api/projects/${projectId}/template/reset`, { method: 'POST' });
      alert('기본 마스터 템플릿으로 복원되었습니다.');
      fetchTemplateInfo();
      onTemplateChanged?.();
    } catch (err) {
      alert('복원 실패: ' + err.message);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileSpreadsheet size={20} color="var(--primary)" />
            <h3 className="modal-title">현장 마스터 엑셀 서식 관리</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '5px' }}>
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* 현재 템플릿 상태 */}
          <div style={{ background: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>현재 적용 중인 마스터 엑셀 서식:</div>
            <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '4px', color: 'var(--text-main)', wordBreak: 'break-all' }}>
              {templateInfo ? templateInfo.filename : '조회 중...'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--success-text)', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={14} color="var(--success)" /> 보고서 생성 시 해당 서식의 시트, 셀 크기, 수식이 100% 매핑됩니다.
            </div>
          </div>

          {/* 파일 업로드 드롭존 */}
          <div 
            className="upload-dropzone"
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              accept=".xlsx,.xlsm" 
              style={{ display: 'none' }}
              onChange={(e) => handleFileUpload(e.target.files)} 
            />
            <UploadCloud size={36} color="var(--primary)" style={{ margin: '0 auto 10px auto' }} />
            <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>
              {uploading ? '서식 파일 업로드 중...' : '새로운 마스터 서식(.xlsx) 업로드'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              클릭하거나 엑셀 파일을 드래그하여 현장 전용 양식을 등록하세요.
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
            <button className="btn btn-secondary" onClick={handleReset} style={{ fontSize: '13px' }}>
              <RotateCcw size={14} /> 기본 서식으로 복원
            </button>
            <button className="btn btn-primary" onClick={onClose}>
              완료
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
