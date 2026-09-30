import React, { useState } from 'react';
import { Settings, X, Save } from 'lucide-react';

export default function ProjectSettingsModal({ isOpen, onClose, project, onSettingsUpdated }) {
  if (!isOpen || !project) return null;

  const currentSettings = project.field_settings || {};
  const [dongText, setDongText] = useState((currentSettings.dong_options || []).join(', '));
  const [hoText, setHoText] = useState((currentSettings.ho_options || []).join(', '));
  const [pipeTypesText, setPipeTypesText] = useState((currentSettings.pipe_types || []).join(', '));
  const [pipeNamesText, setPipeNamesText] = useState((currentSettings.pipe_names || []).join(', '));
  const [defectsText, setDefectsText] = useState((currentSettings.defect_options || []).join(', '));
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    const newSettings = {
      dong_options: dongText.split(',').map(s => s.trim()).filter(Boolean),
      ho_options: hoText.split(',').map(s => s.trim()).filter(Boolean),
      pipe_types: pipeTypesText.split(',').map(s => s.trim()).filter(Boolean),
      pipe_names: pipeNamesText.split(',').map(s => s.trim()).filter(Boolean),
      defect_options: defectsText.split(',').map(s => s.trim()).filter(Boolean),
      position_options: currentSettings.position_options || ["입구", "0.5m", "1.0m", "1.5m", "2.0m", "엘보구간", "출구"]
    };

    try {
      const res = await fetch(`/api/projects/${project.id}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_settings: newSettings })
      });
      if (res.ok) {
        alert('현장 필수 데이터 항목이 저장되었습니다.');
        onSettingsUpdated();
        onClose();
      }
    } catch (err) {
      alert('설정 저장 실패: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: '650px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Settings size={20} color="var(--primary)" />
            <h3 className="modal-title">[{project.name}] 현장 항목 커스텀 설정</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '5px' }}>
            <X size={16} />
          </button>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          💡 현장에 맞게 각 항목을 쉼표(,)로 구분하여 입력하세요. 작업자는 여기에 등록된 항목만 드롭다운에서 선택할 수 있습니다.
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label">동 / 구역 목록</label>
            <textarea 
              className="form-input" 
              rows={3} 
              value={dongText} 
              onChange={(e) => setDongText(e.target.value)} 
            />
          </div>

          <div className="form-group">
            <label className="form-label">호수 / 층 목록</label>
            <textarea 
              className="form-input" 
              rows={3} 
              value={hoText} 
              onChange={(e) => setHoText(e.target.value)} 
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">배관종류 (용도) 목록</label>
          <input 
            type="text" 
            className="form-input" 
            value={pipeTypesText} 
            onChange={(e) => setPipeTypesText(e.target.value)} 
          />
        </div>

        <div className="form-group">
          <label className="form-label">배관명 (부위) 목록</label>
          <textarea 
            className="form-input" 
            rows={2} 
            value={pipeNamesText} 
            onChange={(e) => setPipeNamesText(e.target.value)} 
          />
        </div>

        <div className="form-group">
          <label className="form-label">이상소견 (상태) 목록</label>
          <input 
            type="text" 
            className="form-input" 
            value={defectsText} 
            onChange={(e) => setDefectsText(e.target.value)} 
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
          <button className="btn btn-secondary" onClick={onClose}>취소</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={15} /> {saving ? '저장 중...' : '현장 설정 저장'}
          </button>
        </div>
      </div>
    </div>
  );
}
