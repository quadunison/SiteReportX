import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, Play, CheckCircle2, AlertCircle, Eye, RefreshCw, ZoomIn, 
  Film, Image as ImageIcon, FileSpreadsheet, Terminal, Edit3, Settings2, Download 
} from 'lucide-react';
import ReportPreview from './ReportPreview';
import ProcessLogViewer from './ProcessLogViewer';
import TemplateUploadModal from './TemplateUploadModal';

export default function InspectionWorkspace({ project, onProjectUpdated, onOpenReportModal }) {
  const [activeMode, setActiveMode] = useState('editor'); // 'editor', 'preview', 'logs'
  const [selectedItemIndex, setSelectedItemIndex] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState({ percentage: 0, current: 0, total: 0, status: 'idle' });
  const [localItems, setLocalItems] = useState(project.items || []);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const debounceTimers = useRef({});
  const fileInputRef = useRef(null);

  useEffect(() => {
    setLocalItems(project.items || []);
    if (project.items && project.items.length > 0 && selectedItemIndex >= project.items.length) {
      setSelectedItemIndex(0);
    }
  }, [project]);

  // 주기적 진행률 폴링
  useEffect(() => {
    let interval;
    if (analyzing) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`/api/projects/${project.id}/analyze-progress`);
          const data = await res.json();
          setProgress(data);
          if (data.status === 'completed') {
            setAnalyzing(false);
            onProjectUpdated();
          }
        } catch (err) {
          console.error(err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [analyzing, project.id]);

  const selectedItem = localItems[selectedItemIndex] || null;
  const fieldSettings = project.field_settings || {};

  // 파일 업로드 처리
  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await fetch(`/api/projects/${project.id}/upload`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        onProjectUpdated();
      }
    } catch (err) {
      alert('업로드 실패: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  // AI 분석 시작
  const handleStartAnalysis = async () => {
    setAnalyzing(true);
    try {
      await fetch(`/api/projects/${project.id}/analyze`, { method: 'POST' });
    } catch (err) {
      alert('분석 시작 실패: ' + err.message);
      setAnalyzing(false);
    }
  };

  // 실시간 500ms 디바운스 자동저장
  const handleItemChange = (index, field, value) => {
    const updated = [...localItems];
    updated[index] = { ...updated[index], [field]: value };
    
    // 표준 파일명 자동 갱신
    const it = updated[index];
    const dongStr = it.dong ? `${it.dong}동` : '';
    const hoStr = it.ho ? `${it.ho}호` : '';
    const stdName = `${dongStr} ${hoStr} ${it.pipe_type || ''} ${it.pipe_name || ''}_${it.defect || '정상'}_${it.position || '입구'}`.trim();
    updated[index].standard_filename = stdName;
    setLocalItems(updated);

    const itemId = it.id;
    if (debounceTimers.current[itemId]) {
      clearTimeout(debounceTimers.current[itemId]);
    }

    debounceTimers.current[itemId] = setTimeout(async () => {
      try {
        await fetch(`/api/projects/${project.id}/items/${itemId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ [field]: value, standard_filename: stdName })
        });
      } catch (err) {
        console.error('자동저장 실패:', err);
      }
    }, 500);
  };

  const getMediaUrl = (item) => {
    if (!item) return null;
    const path = item.frame_image_path || item.original_file_path;
    if (!path) return null;
    const filename = path.split(/[\\/]/).pop();
    return `/api/media/${project.id}/${filename}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* 상단 컨트롤 및 모드 네비게이션 */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div>
            <span style={{ fontSize: '18px', fontWeight: 800 }}>{project.name}</span>
            <span className="badge badge-primary" style={{ marginLeft: '10px' }}>
              총 {localItems.length}건
            </span>
          </div>

          {analyzing && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '10px' }}>
              <RefreshCw size={16} className="animate-spin" color="#3B82F6" />
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#60A5FA' }}>
                AI 분석 중 ({progress.current}/{progress.total}건, {progress.percentage}%)
              </span>
              <div style={{ width: '100px', height: '6px', background: '#1E293B', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${progress.percentage}%`, height: '100%', background: '#3B82F6', transition: 'width 0.3s' }} />
              </div>
            </div>
          )}
        </div>

        {/* 3대 작업 모드 탭 전환 버튼 */}
        <div style={{ display: 'flex', background: '#F1F5F9', padding: '4px', borderRadius: '8px', border: '1px solid #CBD5E1' }}>
          <button
            onClick={() => setActiveMode('editor')}
            className="btn"
            style={{
              padding: '7px 15px',
              fontSize: '13px',
              fontWeight: 700,
              borderRadius: '6px',
              background: activeMode === 'editor' ? '#2563EB' : 'transparent',
              color: activeMode === 'editor' ? '#FFFFFF' : '#475569',
              boxShadow: activeMode === 'editor' ? '0 1px 3px rgba(0,0,0,0.15)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <Edit3 size={14} /> ① AI 명판 검수 에디터
          </button>
          <button
            onClick={() => setActiveMode('preview')}
            className="btn"
            style={{
              padding: '7px 15px',
              fontSize: '13px',
              fontWeight: 700,
              borderRadius: '6px',
              background: activeMode === 'preview' ? '#059669' : 'transparent',
              color: activeMode === 'preview' ? '#FFFFFF' : '#475569',
              boxShadow: activeMode === 'preview' ? '0 1px 3px rgba(0,0,0,0.15)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <FileSpreadsheet size={14} /> ② 마스터 엑셀 미리보기
          </button>
          <button
            onClick={() => setActiveMode('logs')}
            className="btn"
            style={{
              padding: '7px 15px',
              fontSize: '13px',
              fontWeight: 700,
              borderRadius: '6px',
              background: activeMode === 'logs' ? '#7C3AED' : 'transparent',
              color: activeMode === 'logs' ? '#FFFFFF' : '#475569',
              boxShadow: activeMode === 'logs' ? '0 1px 3px rgba(0,0,0,0.15)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <Terminal size={14} /> ③ 실시간 작업 로그
          </button>
        </div>

        {/* 우측 상단 액션 버튼군 */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" onClick={() => setIsTemplateModalOpen(true)} title="마스터 엑셀 템플릿 관리">
            <FileSpreadsheet size={16} color="#10B981" /> 마스터 템플릿
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            multiple 
            accept="video/*,image/*" 
            style={{ display: 'none' }} 
            onChange={(e) => handleFileUpload(e.target.files)} 
          />
          <button className="btn btn-secondary" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
            <UploadCloud size={16} /> {uploading ? '업로드 중...' : '영상/사진 추가'}
          </button>
          <button className="btn btn-primary" onClick={handleStartAnalysis} disabled={analyzing || localItems.length === 0}>
            <Play size={16} /> AI 일괄 분석
          </button>
        </div>
      </div>

      {/* 모드 1: 검수 에디터 */}
      {activeMode === 'editor' && (
        <div className="workspace-layout">
          {/* 좌측: 캡처된 명판 사진 돋보기 뷰어 */}
          <div className="preview-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ZoomIn size={16} /> 캡처된 명판 사진
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                마우스 오버 시 돋보기 확대
              </span>
            </div>

            <div className="image-zoom-box">
              {selectedItem ? (
                selectedItem.is_video && !selectedItem.frame_image_path ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                    <Film size={48} style={{ opacity: 0.4, marginBottom: '8px' }} />
                    <span style={{ fontSize: '13px' }}>AI 명판 분석을 실행하면</span>
                    <span style={{ fontSize: '12px' }}>선명한 명판 프레임이 추출됩니다.</span>
                  </div>
                ) : (
                  <img 
                    src={getMediaUrl(selectedItem)} 
                    alt="명판 이미지" 
                    className="zoom-image"
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                )
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                  <ImageIcon size={48} style={{ opacity: 0.4, marginBottom: '8px' }} />
                  <span>항목을 선택하세요</span>
                </div>
              )}
            </div>

            {selectedItem && (
              <div style={{ fontSize: '12px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '6px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ color: 'var(--text-dim)' }}>원본 파일:</div>
                <div style={{ fontWeight: 600, wordBreak: 'break-all' }}>{selectedItem.original_filename}</div>
                <div style={{ color: 'var(--text-dim)', marginTop: '4px' }}>표준 파일명:</div>
                <div style={{ fontWeight: 600, color: '#60A5FA', wordBreak: 'break-all' }}>
                  {selectedItem.standard_filename || '(검수 중)'}
                </div>
              </div>
            )}
          </div>

          {/* 우측: 현장 등록 옵션 드롭다운 검수 테이블 */}
          <div className="table-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px', fontWeight: 700 }}>
                검수 및 수정 테이블 <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 400 }}>(수정 시 500ms 실시간 자동저장)</span>
              </span>
              <span style={{ fontSize: '12px', color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={14} /> 자동저장 활성화됨
              </span>
            </div>

            <div className="table-wrapper">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th style={{ width: '45px' }}>연번</th>
                    <th style={{ width: '90px' }}>동</th>
                    <th style={{ width: '90px' }}>호</th>
                    <th style={{ width: '130px' }}>배관종류</th>
                    <th style={{ width: '140px' }}>배관명</th>
                    <th style={{ width: '120px' }}>이상소견</th>
                    <th style={{ width: '100px' }}>이상위치</th>
                    <th style={{ width: '70px' }}>미리보기</th>
                  </tr>
                </thead>
                <tbody>
                  {localItems.map((item, idx) => {
                    const isSelected = idx === selectedItemIndex;
                    const isDefect = item.defect && item.defect !== '정상' && item.defect !== '' && item.defect !== '-';

                    return (
                      <tr 
                        key={item.id} 
                        className={isSelected ? 'selected' : ''}
                        onClick={() => setSelectedItemIndex(idx)}
                      >
                        <td style={{ fontWeight: 600, color: 'var(--text-dim)' }}>{idx + 1}</td>
                        
                        {/* 동 선택 드롭다운 */}
                        <td>
                          <select 
                            className="select-input"
                            value={item.dong || ''}
                            onChange={(e) => handleItemChange(idx, 'dong', e.target.value)}
                          >
                            <option value="">(선택)</option>
                            {(fieldSettings.dong_options || []).map(opt => (
                              <option key={opt} value={opt}>{opt}동</option>
                            ))}
                          </select>
                        </td>

                        {/* 호 선택 드롭다운 */}
                        <td>
                          <select 
                            className="select-input"
                            value={item.ho || ''}
                            onChange={(e) => handleItemChange(idx, 'ho', e.target.value)}
                          >
                            <option value="">(선택)</option>
                            {(fieldSettings.ho_options || []).map(opt => (
                              <option key={opt} value={opt}>{opt}호</option>
                            ))}
                          </select>
                        </td>

                        {/* 배관종류 드롭다운 */}
                        <td>
                          <select 
                            className="select-input"
                            value={item.pipe_type || ''}
                            onChange={(e) => handleItemChange(idx, 'pipe_type', e.target.value)}
                          >
                            <option value="">(선택)</option>
                            {(fieldSettings.pipe_types || []).map(pt => (
                              <option key={pt} value={pt}>{pt}</option>
                            ))}
                          </select>
                        </td>

                        {/* 배관명 드롭다운 */}
                        <td>
                          <select 
                            className="select-input"
                            value={item.pipe_name || ''}
                            onChange={(e) => handleItemChange(idx, 'pipe_name', e.target.value)}
                          >
                            <option value="">(선택)</option>
                            {(fieldSettings.pipe_names || []).map(pn => (
                              <option key={pn} value={pn}>{pn}</option>
                            ))}
                          </select>
                        </td>

                        {/* 이상소견 드롭다운 (결함 시 하이라이트) */}
                        <td>
                          <select 
                            className={`select-input defect-select ${isDefect ? 'is-defect' : ''}`}
                            value={item.defect || '정상'}
                            onChange={(e) => handleItemChange(idx, 'defect', e.target.value)}
                          >
                            {(fieldSettings.defect_options || ["정상", "물고임", "구배불량", "토사/이물질", "파손/크랙"]).map(df => (
                              <option key={df} value={df}>{df}</option>
                            ))}
                          </select>
                        </td>

                        {/* 이상위치 드롭다운 */}
                        <td>
                          <select 
                            className="select-input"
                            value={item.position || '입구'}
                            onChange={(e) => handleItemChange(idx, 'position', e.target.value)}
                          >
                            {(fieldSettings.position_options || ["입구", "0.5m", "1.0m", "1.5m", "2.0m", "엘보구간", "출구"]).map(pos => (
                              <option key={pos} value={pos}>{pos}</option>
                            ))}
                          </select>
                        </td>

                        {/* 미리보기 뷰어 활성화 버튼 */}
                        <td style={{ textAlign: 'center' }}>
                          <button 
                            className={`btn ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                            style={{ padding: '4px 8px', fontSize: '11px' }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedItemIndex(idx);
                            }}
                          >
                            <Eye size={12} /> 보기
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 모드 2: 마스터 엑셀 실시간 미리보기 */}
      {activeMode === 'preview' && (
        <ReportPreview 
          project={project} 
          onGenerateReport={onOpenReportModal} 
        />
      )}

      {/* 모드 3: 실시간 작업 로그 콘솔 */}
      {activeMode === 'logs' && (
        <ProcessLogViewer 
          projectId={project.id} 
          analyzing={analyzing} 
        />
      )}

      {/* 마스터 템플릿 관리 모달 */}
      <TemplateUploadModal
        isOpen={isTemplateModalOpen}
        onClose={() => setIsTemplateModalOpen(false)}
        projectId={project.id}
        onTemplateChanged={onProjectUpdated}
      />
    </div>
  );
}
