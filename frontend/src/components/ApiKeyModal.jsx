import React, { useState, useEffect } from 'react';
import { Key, X, CheckCircle, AlertCircle } from 'lucide-react';

export default function ApiKeyModal({ isOpen, onClose }) {
  const [keyStatus, setKeyStatus] = useState({
    gemini_configured: false,
    openai_configured: false,
    google_vision_configured: false
  });
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetch('/api/keys')
        .then(res => res.json())
        .then(data => setKeyStatus(data))
        .catch(err => console.error(err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch('/api/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gemini: geminiKey || undefined, openai: openaiKey || undefined })
      });
      alert('API 키가 성공적으로 반영되었습니다.');
      onClose();
    } catch (err) {
      alert('API 키 저장 실패: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={20} color="#3B82F6" />
            <h3 className="modal-title">AI 비전 API 키 설정</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '4px' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ marginBottom: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>
          기존 TaskieX 폴더(`gemini-api-key`, `vision-api-key`, `chatgpt-api-key`)의 키가 자동으로 감지됩니다.
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>Google Cloud Vision API (JSON)</span>
            <span className={`badge ${keyStatus.google_vision_configured ? 'badge-success' : 'badge-neutral'}`}>
              {keyStatus.google_vision_configured ? '감지됨 ✓' : '미설정'}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>Google Gemini 1.5 Flash API</span>
            <span className={`badge ${keyStatus.gemini_configured ? 'badge-success' : 'badge-neutral'}`}>
              {keyStatus.gemini_configured ? '감지됨 ✓' : '미설정'}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>OpenAI GPT-4o-mini API</span>
            <span className={`badge ${keyStatus.openai_configured ? 'badge-success' : 'badge-neutral'}`}>
              {keyStatus.openai_configured ? '감지됨 ✓' : '미설정'}
            </span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Gemini API 키 임시 입력 (선택)</label>
          <input 
            type="password" 
            className="form-input" 
            placeholder="AIzaSy..." 
            value={geminiKey} 
            onChange={(e) => setGeminiKey(e.target.value)} 
          />
        </div>

        <div className="form-group">
          <label className="form-label">OpenAI API 키 임시 입력 (선택)</label>
          <input 
            type="password" 
            className="form-input" 
            placeholder="sk-proj-..." 
            value={openaiKey} 
            onChange={(e) => setOpenaiKey(e.target.value)} 
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
          <button className="btn btn-secondary" onClick={onClose}>취소</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '저장 중...' : '확인'}
          </button>
        </div>
      </div>
    </div>
  );
}
