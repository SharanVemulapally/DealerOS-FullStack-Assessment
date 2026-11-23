import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

function App(){
  const [org,setOrg]=useState('ORG-A'), [reason,setReason]=useState(''), [sort,setSort]=useState('-value');
  const [data,setData]=useState([]), [error,setError]=useState(''), [loading,setLoading]=useState(false);
  async function load(){
    setLoading(true); setError('');
    try{
      const params=new URLSearchParams({org,sort}); if(reason) params.set('reason',reason);
      const response=await fetch(`http://127.0.0.1:8000/api/disagreements/?${params}`);
      const body=await response.json(); if(!response.ok) throw new Error(body.error||'API request failed');
      setData(body.results||[]);
    }catch(e){setError(e.message);setData([])} finally{setLoading(false)}
  }
  useEffect(()=>{load()},[org,reason,sort]);
  const money=v=>v===null||v===undefined?'':Array.isArray(v)?v.join(' + '):Number(v).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2});
  return <main>
    <header><div><p className="eyebrow">DEALEROS · DATA RECONCILIATION</p><h1>Disagreement Monitor</h1><p className="sub">Compare System A and System B without crossing tenant boundaries.</p></div><span className="status">● Local workspace</span></header>
    <section className="toolbar">
      <label>Organization<select value={org} onChange={e=>setOrg(e.target.value)}><option>ORG-A</option><option>ORG-B</option></select></label>
      <label>Reason<select value={reason} onChange={e=>setReason(e.target.value)}><option value="">All reasons</option>{['MISSING_IN_B','ORPHAN_IN_B','DUPLICATE_IN_B','VALUE_MISMATCH','LOCATION_MISMATCH','DATE_MISMATCH'].map(x=><option key={x}>{x}</option>)}</select></label>
      <button onClick={()=>setSort(s=>s==='value'?'-value':'value')}>Sort value {sort==='-value'?'↓':'↑'}</button>
      <button className="refresh" onClick={load}>↻ Refresh</button>
    </section>
    <section className="summary"><div><span>Organization</span><strong>{org}</strong></div><div><span>Disagreements</span><strong>{data.length}</strong></div><div><span>View</span><strong>{reason||'All reasons'}</strong></div></section>
    {error&&<div className="error">Cannot load data: {error}. Start the Django API and run the CSV importer.</div>}
    <section className="tablewrap"><div className="tablehead"><h2>Reconciliation results</h2><span>{loading?'Loading…':`${data.length} rows`}</span></div>
    <table><thead><tr><th>Reason</th><th>Record ID</th><th>Location</th><th>System A value</th><th>System B value</th><th>Difference</th></tr></thead>
    <tbody>{data.map((r,i)=><tr key={i}><td><span className="pill">{r.reason}</span></td><td className="mono">{r.record_id||'—'}</td><td>{r.location||'—'}</td><td>{money(r.a_value)}</td><td>{money(r.b_value)}</td><td>{r.a_value!=null&&r.b_value!=null&&!Array.isArray(r.b_value)?money(Math.abs(Number(r.a_value)-Number(r.b_value))):'—'}</td></tr>)}
    {!loading&&data.length===0&&<tr><td colSpan="6" className="empty">No disagreements found for this selection.</td></tr>}</tbody></table></section>
    <footer>DealerOS assessment · SQLite · Django REST API · React</footer>
  </main>
}
createRoot(document.getElementById('root')).render(<App/>);
