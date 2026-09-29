import React, { useState, useEffect } from 'react';
import { Plus, FolderOpen, AlertTriangle, CheckCircle, Calendar, ArrowRight, Building } from 'lucide-react';

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.5px' }}>건설 현장 프로젝트 관리</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            작업 중인 현장을 선택하여 이어하거나 새 배관 검사 현장을 생성하세요.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)} style={{ padding: '10px 20px' }}>
          <Plus size={18} /> 새 현장 프로젝트 생성
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>현장 목록을 불러오는 중...</div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Building size={48} color="#3B82F6" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '8px' }}>등록된 현장이 없습니다</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            첫 번째 배관 검사 현장 프로젝트를 생성하여 시작해 보세요.
          </p>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <Plus size={16} /> 새 현장 만들기
          </button>
        </div>
      ) : (
        <div className="dashboard-grid">
          {projects.map((p) => (
            <div key={p.id} className="project-card" onClick={() => onSelectProject(p.id)}>
              <div className="project-card-header">
                <span className="project-name">{p.name}</span>
                <span className="badge badge-primary">작업 중</span>
              </div>

              <div className="project-stats">
                <div className="stat-item">
                  <span className="stat-label">총 검사 항목</span>
                  <span className="stat-value" style={{ color: '#60A5FA' }}>{p.total_items}건</span>
                </div>
                <div className="stat-item" style={{ marginLeft: 'auto' }}>
                  <span className="stat-label">이상 배관 발견</span>
                  <span className="stat-value" style={{ color: p.defect_count > 0 ? '#F59E0B' : '#10B981' }}>
                    {p.defect_count}건
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-dim)' }}>
                  <Calendar size={12} /> {p.created_at?.slice(0, 10)}
                </div>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#3B82F6', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  열기 / 이어하기 <ArrowRight size={13} />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 새 현장 생성 모달 */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3 className="modal-title">새 배관 검사 현장 생성</h3>
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
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '20px' }}>
                생성 후 현장 설정에서 동/호수 및 배관명 목록을 자유롭게 커스텀할 수 있습니다.
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>취소</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? '생성 중...' : '현장 생성 및 시작'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
