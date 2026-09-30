import React, { useState, useEffect } from 'react';
import { Plus, AlertTriangle, CheckCircle2, Calendar, ArrowRight, Building2, HardHat, FileSpreadsheet } from 'lucide-react';

export default function ProjectDashboard({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchProjects = async () => {
    try {
      const res = await fetch('/api/projects');
      const data = await res.json();
      setProjects(data);
    } catch (err) {
      console.error('프로젝트 목록 조회 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    setCreating(true);
    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newProjectName.trim() })
      });
      const data = await res.json();
      if (res.ok) {
        setShowCreateModal(false);
        setNewProjectName('');
        onSelectProject(data.id);
      }
    } catch (err) {
      alert('프로젝트 생성 실패: ' + err.message);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      {/* 대시보드 타이틀 영역 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '28px', borderBottom: '1px solid var(--border-color)', paddingBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <HardHat size={20} color="var(--primary)" />
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary)', letterSpacing: '-0.01em' }}>현장 관리 콘솔</span>
          </div>
          <h2 style={{ fontSize: '26px', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--text-main)' }}>배관 내시경 검사 프로젝트</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            현장을 선택하여 AI 검수를 이어하거나 신규 공사 현장을 등록하세요.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)} style={{ padding: '9px 18px', fontSize: '14px' }}>
          <Plus size={16} /> 신규 현장 등록
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '14px', fontWeight: 600 }}>현장 프로젝트 목록을 불러오는 중입니다...</div>
        </div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '64px 20px', maxWidth: '520px', margin: '40px auto' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'var(--primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--primary)' }}>
            <Building2 size={28} />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '8px', color: 'var(--text-main)' }}>등록된 현장이 없습니다</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '24px', lineHeight: 1.6 }}>
            첫 번째 배관 검사 현장 프로젝트를 생성하여 동영상 및 사진을 업로드해 보세요.
          </p>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <Plus size={16} /> 신규 현장 등록하기
          </button>
        </div>
      ) : (
        <div className="dashboard-grid">
          {projects.map((p) => {
            const hasDefect = p.defect_count > 0;
            return (
              <div key={p.id} className="project-card" onClick={() => onSelectProject(p.id)}>
                <div className="project-card-header">
                  <span className="project-name">{p.name}</span>
                  <span className="badge badge-neutral">
                    작업 진행 중
                  </span>
                </div>

                <div className="project-stats">
                  <div className="stat-item">
                    <span className="stat-label">총 검사항목</span>
                    <span className="stat-value" style={{ color: 'var(--text-main)' }}>{p.total_items}건</span>
                  </div>
                  <div className="stat-item" style={{ marginLeft: 'auto' }}>
                    <span className="stat-label">이상 배관</span>
                    <span className="stat-value" style={{ color: hasDefect ? 'var(--warning-text)' : 'var(--success-text)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {hasDefect ? <AlertTriangle size={15} color="var(--warning)" /> : <CheckCircle2 size={15} color="var(--success)" />}
                      {p.defect_count}건
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid #F1F5F9' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-dim)', fontVariantNumeric: 'tabular-nums' }}>
                    <Calendar size={13} /> {p.created_at?.slice(0, 10)}
                  </div>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    검수 에디터 열기 <ArrowRight size={13} />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 새 현장 생성 모달 */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3 className="modal-title">신규 배관 검사 현장 등록</h3>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">현장명 (공사명)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="예: 마포자이 1단지 배관내시경 검사" 
                  value={newProjectName} 
                  onChange={(e) => setNewProjectName(e.target.value)} 
                  autoFocus 
                  required 
                />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '22px', lineHeight: 1.5 }}>
                • 현장 생성 후 상단 설정 메뉴에서 동/호수 및 배관명 목록을 자유롭게 커스텀할 수 있습니다.
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>취소</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? '등록 중...' : '현장 생성 및 시작'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
