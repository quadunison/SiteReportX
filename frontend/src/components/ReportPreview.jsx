import React, { useState } from 'react';
import { FileSpreadsheet, Download, AlertTriangle, CheckCircle2, Eye, ExternalLink } from 'lucide-react';

export default function ReportPreview({ project, onGenerateReport }) {
  const [activeTab, setActiveTab] = useState('입상관');
  const items = project.items || [];
  const todayStr = new Date().toISOString().split('T')[0].replace(/-/g, '.');

  // 배관종류별 분류
  const categorized = {
    '입상관': [],
    '세대매립관': [],
    '세대PD': [],
    '세대층상배관': []
  };

  items.forEach(it => {
    const pt = (it.pipe_type || '').replace(/\s+/g, '');
    let matched = '세대매립관';
    for (const key of Object.keys(categorized)) {
      if (pt.includes(key) || key.includes(pt)) {
        matched = key;
        break;
      }
    }
    if (!categorized[matched]) {
      matched = pt.includes('입상') ? '입상관' : '세대매립관';
    }
    categorized[matched].push(it);
  });

  const activeItems = categorized[activeTab] || [];
  const totalDefects = items.filter(it => it.defect && it.defect !== '정상' && it.defect !== '').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* 상단 컨트롤 및 표지 요약 */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileSpreadsheet size={20} color="#10B981" />
            <span style={{ fontSize: '18px', fontWeight: 800 }}>
              [{project.name}] 배관내시경 마스터 보고서 실시간 미리보기
            </span>
          </div>
          <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
            서식: <strong style={{ color: '#60A5FA' }}>master_sample_0416.xlsx</strong> | 총 {items.length}건 중 결함 {totalDefects}건 감지 | 작성일: {todayStr}
          </div>
        </div>

        <button className="btn btn-primary" onClick={onGenerateReport}>
          <Download size={16} /> 실무 마스터 엑셀 및 미디어 ZIP 다운로드
        </button>
      </div>

      {/* 배관종류별 시트 탭 네비게이션 */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
        {Object.keys(categorized).map(cat => {
          const count = categorized[cat].length;
          const defectCount = categorized[cat].filter(i => i.defect && i.defect !== '정상' && i.defect !== '').length;
          const isActive = activeTab === cat;

          return (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`btn ${isActive ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '8px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <span>3.이상배관LIST_{cat}</span>
              <span style={{ 
                background: isActive ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)', 
                padding: '2px 8px', 
                borderRadius: '10px',
                fontSize: '11px',
                fontWeight: 700 
              }}>
                {count}건 {defectCount > 0 && <span style={{ color: '#EF4444' }}>({defectCount}개 결함)</span>}
              </span>
            </button>
          );
        })}
      </div>

      {/* 엑셀 시트 100% 매핑 미리보기 테이블 */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', background: '#0F172A', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontWeight: 700, fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#10B981' }}>■</span> {activeTab} 이상배관 LIST (엑셀 인쇄 서식 규격)
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            * F열 사진은 엑셀 저장 시 1px 여백으로 가득 채워져 삽입됩니다.
          </span>
        </div>

        <div className="table-wrapper" style={{ maxHeight: '600px', overflowY: 'auto' }}>
          <table className="custom-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#1E3A8A', color: '#FFFFFF', textAlign: 'center' }}>
                <th style={{ width: '45px', padding: '10px' }}>NO</th>
                <th style={{ width: '90px' }}>점검일</th>
                <th style={{ width: '80px' }}>동명</th>
                <th style={{ width: '80px' }}>호수(라인)</th>
                <th style={{ width: '140px' }}>배관명</th>
                <th style={{ width: '220px' }}>이상배관 이미지 (F열 정밀 삽입)</th>
                <th style={{ width: '110px' }}>이상위치</th>
                <th style={{ width: '130px' }}>이상소견</th>
                <th style={{ width: '90px' }}>보고일</th>
              </tr>
            </thead>
            <tbody>
              {activeItems.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    해당 배관종류({activeTab})로 등록된 검사 데이터가 없습니다.
                  </td>
                </tr>
              ) : (
                activeItems.map((it, idx) => {
                  const isDefect = it.defect && it.defect !== '정상' && it.defect !== '' && it.defect !== '-';
                  const imgSrc = it.frame_image_path ? `/api/media/${project.id}/${it.frame_image_path.split(/[\\/]/).pop()}` : null;

                  return (
                    <tr key={it.id} style={{ height: '140px', borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ textAlign: 'center', fontWeight: 600, color: 'var(--text-muted)' }}>{idx + 1}</td>
                      <td style={{ textAlign: 'center' }}>{todayStr}</td>
                      <td style={{ textAlign: 'center', fontWeight: 700 }}>{it.dong ? `${it.dong}동` : '-'}</td>
                      <td style={{ textAlign: 'center', fontWeight: 700 }}>{it.ho ? `${it.ho}호` : '-'}</td>
                      <td style={{ textAlign: 'center', fontWeight: 600 }}>{it.pipe_name || '-'}</td>
                      
                      {/* F열 이미지 영역 */}
                      <td style={{ padding: '6px', textAlign: 'center', verticalAlign: 'middle' }}>
                        {imgSrc ? (
                          <div style={{ width: '200px', height: '130px', margin: '0 auto', borderRadius: '4px', overflow: 'hidden', border: '1px solid #334155', background: '#000' }}>
                            <img 
                              src={imgSrc} 
                              alt="배관사진" 
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                            />
                          </div>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>(이미지 추출 중)</span>
                        )}
                      </td>

                      <td style={{ textAlign: 'center', fontWeight: 600 }}>{it.position || '입구'}</td>
                      
                      {/* H열 이상소견 (결함 시 하이라이트) */}
                      <td style={{ 
                        textAlign: 'center', 
                        fontWeight: 700,
                        background: isDefect ? '#FEF08A' : 'transparent',
                        color: isDefect ? '#DC2626' : 'var(--text-main)'
                      }}>
                        {it.defect || '정상'}
                      </td>

                      <td style={{ textAlign: 'center' }}>{todayStr}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
