import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Trash2, RefreshCw, Copy, Check } from 'lucide-react';

export default function ProcessLogViewer({ projectId, analyzing }) {
  const [logs, setLogs] = useState([]);
  const [copied, setCopied] = useState(false);
  const logEndRef = useRef(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/projects/${projectId}/logs`);
      const data = await res.json();
      if (data.status === 'success') {
        setLogs(data.logs || []);
      }
    } catch (err) {
      console.error('로그 조회 실패:', err);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, analyzing ? 800 : 2500);
    return () => clearInterval(interval);
  }, [projectId, analyzing]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleClearLogs = async () => {
    if (!window.confirm('작업 로그를 초기화하시겠습니까?')) return;
    try {
      await fetch(`/api/projects/${projectId}/logs`, { method: 'DELETE' });
      setLogs([]);
    } catch (err) {
      alert('로그 초기화 실패: ' + err.message);
    }
  };

  const handleCopyLogs = () => {
    const text = logs.map(l => `[${l.time}] ${l.message}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLogStyle = (level) => {
    switch (level) {
      case 'success':
        return { color: '#10B981', fontWeight: 600 };
      case 'error':
        return { color: '#EF4444', fontWeight: 600 };
      case 'warning':
        return { color: '#F59E0B', fontWeight: 600 };
      case 'header':
        return { color: '#60A5FA', fontWeight: 700, borderTop: '1px dashed #334155', borderBottom: '1px dashed #334155', padding: '4px 0', margin: '4px 0' };
      default:
        return { color: '#E2E8F0' };
    }
  };

  return (
    <div className="card" style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Terminal size={18} color="var(--primary)" />
          <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>실시간 분석 및 작업 로그</span>
          {analyzing && (
            <span className="badge badge-primary" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <RefreshCw size={12} className="animate-spin" /> 기록 중
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={handleCopyLogs}>
            {copied ? <Check size={14} color="var(--success)" /> : <Copy size={14} />} {copied ? '복사 완료' : '전체 복사'}
          </button>
          <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px', color: 'var(--danger)' }} onClick={handleClearLogs}>
            <Trash2 size={14} /> 로그 지우기
          </button>
        </div>
      </div>

      <div 
        style={{
          background: '#0F172A',
          borderRadius: '8px',
          border: '1px solid #1E293B',
          padding: '16px',
          fontFamily: 'Consolas, Monaco, monospace',
          fontSize: '12.5px',
          lineHeight: '1.6',
          height: '420px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '2px'
        }}
      >
        {logs.length === 0 ? (
          <div style={{ color: '#64748B', textAlign: 'center', marginTop: '160px' }}>
            기록된 작업 로그가 없습니다. [AI 명판 일괄 분석] 또는 [보고서 생성]을 실행하면 실시간 피드백이 출력됩니다.
          </div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
              <span style={{ color: '#64748B', flexShrink: 0, userSelect: 'none' }}>[{log.time}]</span>
              <span style={{ ...getLogStyle(log.level), wordBreak: 'break-all', flexGrow: 1 }}>
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
