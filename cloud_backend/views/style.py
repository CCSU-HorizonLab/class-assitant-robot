"""Shared Phase 3.1 visual tokens for cloud HTML pages."""
from __future__ import annotations


PHASE31_STYLE = """
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    *, *::before, *::after { box-sizing: border-box; }
    :root {
      --color-bg: #F8FAFC;
      --color-surface: rgba(255, 255, 255, 0.85);
      --color-surface-soft: rgba(248, 250, 252, 0.7);
      --color-surface-tint: rgba(239, 246, 255, 0.8);
      --color-border: rgba(226, 232, 240, 0.8);
      --color-border-soft: rgba(241, 245, 249, 0.6);
      --color-text: #0F172A;
      --color-text-muted: #475569;
      --color-text-subtle: #64748B;
      --color-primary: #3B82F6;
      --color-primary-strong: #1D4ED8;
      --color-primary-soft: #EFF6FF;
      --color-secondary: #10B981;
      --color-secondary-soft: #ECFDF5;
      --color-teaching: #8B5CF6;
      --color-teaching-soft: #F5F3FF;
      --color-warm: #F59E0B;
      --color-warm-soft: #FEF3C7;
      --color-success: #10B981;
      --color-success-soft: #ECFDF5;
      --color-warning: #F59E0B;
      --color-warning-soft: #FEF3C7;
      --color-danger: #EF4444;
      --color-danger-soft: #FEE2E2;
      --color-info: #0EA5E9;
      --color-info-soft: #E0F2FE;
      --chart-attention: #3B82F6;
      --chart-activity: #10B981;
      --chart-question: #F59E0B;
      --chart-stage-summary: #8B5CF6;
      --chart-stage-discussion: #06B6D4;
      --chart-stage-exposition: #3B82F6;
      --chart-stage-management: #64748B;
      --chart-risk: #EF4444;
      --chart-neutral: #64748B;
      --radius-card: 16px;
      --radius-media: 12px;
      --radius-button: 10px;
      --radius-chip: 999px;
      --sidebar-width: 260px;
      --topbar-height: 72px;
      --page-pad-x: 32px;
      --page-pad-y: 28px;
      --section-gap: 28px;
      --grid-gap: 20px;
      --shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02);
      --shadow-hover: 0 20px 40px -15px rgba(15, 23, 42, 0.08), 0 1px 5px rgba(15, 23, 42, 0.03);
      --bg: var(--color-bg);
      --panel: var(--color-surface);
      --line: var(--color-border);
      --text: var(--color-text);
      --muted: var(--color-text-muted);
      --brand: var(--color-primary);
      --brand-2: var(--color-secondary);
      --attention: var(--chart-attention);
      --activity: var(--chart-activity);
      --question: var(--chart-question);
      --risk: var(--chart-risk);
      --success: var(--color-success);
      --warning: var(--color-warning);
      --danger: var(--color-danger);
      --slate: var(--chart-neutral);
    }
    html { width: 100%; min-height: 100%; overflow-y: auto; scroll-behavior: smooth; }
    body {
      margin: 0;
      width: 100%;
      min-height: 100%;
      overflow-y: auto;
      font-family: 'Plus Jakarta Sans', Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
      background-color: var(--color-bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.08) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.05) 0px, transparent 50%),
        radial-gradient(circle at 18px 18px, rgba(59, 130, 246, 0.025) 1px, transparent 1.6px);
      background-size: 100% 100%, 100% 100%, 100% 100%, 28px 28px;
      color: var(--text);
      font-size: 14px;
      line-height: 1.65;
    }
    h1, h2, h3, p { overflow-wrap: anywhere; }
    h1 { font-size: 28px; line-height: 1.25; font-weight: 800; margin: 0 0 10px; letter-spacing: -0.02em; }
    h2 { font-size: 20px; line-height: 1.3; font-weight: 700; margin: 0 0 12px; letter-spacing: -0.01em; }
    h3 { font-size: 16px; line-height: 1.35; font-weight: 700; margin: 0 0 10px; }
    
    /* Sleek Custom Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.3); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.5); }

    .page, .app-shell { width: 100%; max-width: 1480px; margin: 0 auto; padding: var(--page-pad-y) var(--page-pad-x); overflow: visible; }
    .page:has(> .nav) {
      max-width: none;
      min-height: 100vh;
      display: grid;
      grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
      align-items: start;
      column-gap: 28px;
    }
    .page:has(> .nav) > :not(.nav) { grid-column: 2; min-width: 0; width: 100%; }
    .page-main { display: grid; gap: var(--section-gap); width: 100%; min-width: 0; }
    
    /* Glassmorphic Sidebar */
    .nav {
      display: flex; flex-direction: column; align-items: stretch; justify-content: flex-start; gap: 18px;
      min-height: calc(100vh - 56px);
      padding: 24px 16px; border-radius: var(--radius-card); 
      background: rgba(255, 255, 255, 0.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--color-border); box-shadow: var(--shadow);
      position: sticky; top: 28px; z-index: 20;
      width: 100%;
    }
    .page:has(> .nav) > .nav { grid-column: 1; grid-row: 1 / span 999; }
    .nav strong { display: block; font-size: 16px; line-height: 1.35; letter-spacing: -0.01em; color: #0f172a; margin-bottom: 12px; font-weight: 800; }
    .nav strong::before { content: "▦"; display: inline-grid; place-items: center; width: 32px; height: 32px; margin-right: 8px; border-radius: 10px; background: linear-gradient(135deg, var(--color-primary), var(--color-teaching)); color: #fff; font-size: 16px; vertical-align: middle; }
    .nav-links { display: flex; flex-direction: column; gap: 6px; }
    .nav a {
      color: #475569; text-decoration: none; font-weight: 600; padding: 10px 14px;
      border-radius: var(--radius-button); transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex; align-items: center; gap: 8px;
    }
    .nav a.active, .nav a:hover { background: var(--color-primary-soft); color: var(--color-primary-strong); transform: translateX(4px); }
    .identity { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; color: var(--muted); font-size: 13px; }
    .nav .identity { margin-top: auto; padding-top: 14px; border-top: 1px solid var(--color-border-soft); }
    .logout { border: 0; border-radius: var(--radius-button); padding: 8px 14px; font-weight: 700; cursor: pointer; background: #0f172a; color: #fff; transition: all 0.2s ease; }
    .logout:hover { background: #1e293b; transform: translateY(-1px); }

    .badge, .status-pill {
      display: inline-flex; align-items: center; min-height: 24px; border-radius: var(--radius-chip); padding: 0 12px; font-size: 12px;
      font-weight: 700; background: var(--color-primary-soft); color: var(--brand);
    }
    .badge.raw, .status-pill.warning, .badge.medium { background: #fff7ed; color: var(--warning); }
    .badge.reviewed, .badge.low, .status-pill.online, .status-pill.ok, .status-pill.ready { background: #ecfdf5; color: var(--success); }
    .badge.archived, .badge.unknown { background: #f1f5f9; color: var(--slate); }
    .badge.high, .status-pill.offline, .status-pill.missing { background: #fee2e2; color: var(--danger); }
    
    /* Topbar Glass */
    .hero, .page-header, .top-context {
      min-height: var(--topbar-height);
      padding: 24px 28px; border-radius: var(--radius-card);
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--color-border); box-shadow: var(--shadow); color: var(--text);
      position: relative;
      overflow: clip;
    }
    .hero::after, .page-header::after, .top-context::after {
      content: "";
      position: absolute;
      right: 20px;
      top: 20px;
      width: 160px;
      height: 72px;
      pointer-events: none;
      opacity: .25;
      background:
        linear-gradient(90deg, rgba(59,130,246,.15) 1px, transparent 1px),
        linear-gradient(180deg, rgba(16,185,129,.15) 1px, transparent 1px);
      background-size: 18px 18px;
      mask-image: linear-gradient(90deg, transparent, #000 28%, #000);
      -webkit-mask-image: linear-gradient(90deg, transparent, #000 28%, #000);
    }
    .hero .muted { color: var(--muted); }
    .hero h1, .page-header h1 {
      font-size: 28px; line-height: 1.25; font-weight: 800;
      background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .kicker { color: var(--brand); font-size: 12px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
    
    .grid, .metric-grid, .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--grid-gap); margin-top: var(--section-gap); min-width: 0; }
    .metric-grid, #metric-grid, #overview { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
    .record-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; min-width: 0; }
    .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px; margin-top: var(--section-gap); min-width: 0; }
    .two-col, .dashboard-grid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 24px; margin-top: var(--section-gap); align-items: start; min-width: 0; }
    .chart-side-grid { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(320px, .85fr); gap: 20px; margin-top: var(--section-gap); min-width: 0; }
    .dashboard-main, .dashboard-side { min-width: 0; display: grid; gap: 16px; align-content: start; }
    .dashboard-wide { grid-column: 1 / -1; }
    
    /* Modern Glassmorphic Cards */
    .card, .chart-panel, .insight-panel, .evidence-panel, .report-card, .action-card, .result-card {
      background: var(--panel); border: 1px solid rgba(226, 232, 240, 0.8); border-radius: var(--radius-card); padding: 24px;
      box-shadow: var(--shadow); min-width: 0; overflow-wrap: anywhere;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      animation: phase31b-rise .5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .card:hover, .report-card:hover, .action-card:hover, .result-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-hover);
      border-color: rgba(59, 130, 246, 0.25);
    }
    
    .evidence-panel { background: linear-gradient(145deg, #0f172a, #1e293b); color: #f8fafc; border: 1px solid rgba(255,255,255,0.05); }
    .evidence-panel .muted { color: #94a3b8; }
    .insight-panel { background: linear-gradient(135deg, rgba(239, 246, 255, 0.4), #ffffff); border-left: 4px solid var(--brand); }
    .action-card { border-left: 4px solid var(--question); }
    
    /* Metric Card Styling */
    .metric {
      background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(226, 232, 240, 0.8); border-radius: var(--radius-card); padding: 20px; min-height: 112px; position: relative; overflow: clip;
      transition: all 0.2s ease;
    }
    .metric:hover {
      transform: translateY(-2px);
      border-color: rgba(59, 130, 246, 0.2);
      box-shadow: 0 12px 24px -10px rgba(59, 130, 246, 0.1);
    }
    .metric::before { content: ""; position: absolute; left: 20px; top: 14px; width: 32px; height: 4px; border-radius: 999px; background: linear-gradient(90deg, var(--color-primary), var(--color-secondary)); }
    .metric span { display: block; color: var(--muted); font-size: 13px; font-weight: 700; margin-bottom: 8px; }
    .metric strong, .metric-value { font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1.05; letter-spacing: -0.02em; }
    
    .muted { color: var(--muted); }
    .error { color: var(--danger); font-weight: 800; }
    
    /* Sleek Button Overhaul */
    .button, button, .link-button {
      display: inline-flex; align-items: center; justify-content: center; gap: 6px; border: 0; border-radius: var(--radius-button); padding: 10px 18px;
      background: var(--brand); color: #fff; text-decoration: none; font-weight: 600; cursor: pointer;
      white-space: nowrap; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    .button:hover, button:hover { background: var(--color-primary-strong); transform: translateY(-1px); box-shadow: 0 6px 16px rgba(59, 130, 246, 0.25); }
    .button.secondary, .link-button, .action-button { background: rgba(241, 245, 249, 0.8); color: #334155; box-shadow: none; }
    .button.secondary:hover, .link-button:hover, .action-button:hover { background: #e2e8f0; color: #0f172a; transform: translateY(-1px); }
    .danger-light { background: #fee2e2; color: #b91c1c; }
    
    .table-scroll { width: 100%; max-width: 100%; overflow-x: auto; overflow-y: visible; border-radius: var(--radius-card); border: 1px solid var(--color-border); }
    table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 760px; }
    th, td { text-align: left; padding: 14px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
    th { color: var(--muted); font-size: 12px; font-weight: 700; background: #f8fafc; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #e2e8f0; }
    tr:hover td { background-color: #f8fafc; }
    tr:last-child td { border-bottom: none; }
    
    .filters { display: flex; flex-wrap: wrap; gap: 12px; align-items: end; }
    label { display: block; color: var(--muted); font-size: 13px; margin-bottom: 6px; font-weight: 700; }
    select, input { min-width: 160px; border: 1px solid #cbd5e1; border-radius: var(--radius-button); padding: 10px 14px; background: #fff; outline: none; transition: border-color 0.2s; }
    select:focus, input:focus { border-color: var(--brand); }
    
    .empty { border: 1px dashed #cbd5e1; border-radius: var(--radius-card); padding: 24px; color: var(--muted); background: #f8fafc; text-align: center; }
    .list { display: grid; gap: 12px; }
    .record, .result-card { border: 1px solid #e2e8f0; border-radius: var(--radius-card); padding: 16px; background: #fff; min-width: 0; }
    .record-head { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .action-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    td .button, td button, td .action-button { margin: 2px 4px 2px 0; }
    
    .pipeline { display: inline-flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; align-items: center; background: rgba(255, 255, 255, 0.65); padding: 6px 14px; border-radius: 999px; border: 1px solid rgba(59, 130, 246, 0.18); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
    .pipeline span, .pipeline-node { display: inline-flex; align-items: center; gap: 6px; background: #ffffff; color: var(--color-primary-strong); border-radius: 999px; padding: 5px 13px; font-weight: 700; font-size: 12px; border: 1px solid rgba(226, 232, 240, 0.9); box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03); transition: all 0.2s ease; }
    .pipeline span:hover, .pipeline-node:hover { transform: translateY(-1px); border-color: var(--brand); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.12); }
    .pipeline-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--color-secondary); box-shadow: 0 0 8px var(--color-secondary); animation: pulseDot 2s infinite; }
    .pipeline-arrow { color: var(--color-primary); font-size: 13px; font-weight: 800; opacity: 0.8; margin: 0 2px; }
    @keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.35); opacity: 0.5; } }
    
    .chart, .chart-box { height: 340px; min-height: 320px; width: 100%; min-width: 0; }
    .chart-hero { height: 400px; min-height: 380px; }
    .warning { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 12px; padding: 14px; margin-top: 14px; }
    .insight-card { background: linear-gradient(135deg, rgba(239, 246, 255, 0.4), #ffffff); border-left: 4px solid var(--brand); }
    
    .data-strip, .timeline-strip, .heat-strip { display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; margin: 12px 0; }
    .strip-cell { height: 22px; border-radius: 6px; background: #dbeafe; position: relative; overflow: hidden; }
    .strip-cell.low { background: #fee2e2; }
    .strip-cell.medium { background: #fef3c7; }
    .strip-cell.high { background: #dcfce7; }
    .strip-cell.question::after { content: ""; position: absolute; inset: 4px; border-radius: 999px; background: var(--question); opacity: .9; }
    
    .flow-board { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 16px; }
    .flow-step { border: 1px solid rgba(59, 130, 246, 0.15); border-radius: var(--radius-card); padding: 16px; background: rgba(255,255,255,0.85); position: relative; min-width: 0; }
    .flow-step::before { content: ""; width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; background: var(--success); box-shadow: 0 0 0 5px rgba(16,185,129,0.15); }
    .flow-step.warning::before, .flow-step.stale::before, .flow-step.inferred::before { background: var(--warning); box-shadow: 0 0 0 5px rgba(245,158,11,0.15); }
    .flow-step.missing::before, .flow-step.offline::before, .flow-step.failed::before { background: var(--danger); box-shadow: 0 0 0 5px rgba(239,68,68,0.15); }
    
    .progress-track { height: 10px; border-radius: 999px; background: #e2e8f0; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--brand), var(--activity)); }
    .rank-bar { display: grid; gap: 8px; }
    .rank-item { display: grid; grid-template-columns: minmax(0,1fr) 82px; gap: 10px; align-items: center; }
    .rank-line { height: 10px; border-radius: 999px; background: #e2e8f0; overflow: hidden; }
    .rank-line span { display: block; height: 100%; background: linear-gradient(90deg, var(--brand), var(--brand-2)); }
    
    .large-score { font-size: 52px; line-height: 1; font-weight: 800; color: var(--color-primary-strong); letter-spacing: -0.03em; }
    .insight-item { padding: 16px; border-radius: var(--radius-card); background: rgba(248, 250, 252, 0.8); border: 1px solid var(--color-border-soft); }
    
    .visual-badge { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: var(--radius-chip); background: rgba(255,255,255,0.9); color: var(--color-text); font-size: 12px; font-weight: 700; box-shadow: var(--shadow); border: 1px solid var(--color-border); }
    .context-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; position: relative; z-index: 1; }
    .context-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .hero > *, .page-header > *, .top-context > * { position: relative; z-index: 1; }
    .section-title { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-bottom: 12px; }
    .panel-note { color: var(--muted); font-size: 13px; margin: -4px 0 12px; }
    .split-visual { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 20px; align-items: stretch; min-width: 0; }
    .teaching-hero { min-height: 280px; display: grid; align-content: center; }
    .priority-list { display: grid; gap: 10px; }
    .priority-card { display: grid; gap: 6px; padding: 16px; border-radius: var(--radius-card); background: rgba(248, 250, 252, 0.8); border: 1px solid var(--color-border-soft); }
    
    .result-card { display: grid; gap: 10px; min-height: 178px; transition: .18s ease; }
    .result-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-hover); }
    .result-card .score-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .mini-stat { border-radius: 10px; padding: 9px 12px; background: rgba(248, 250, 252, 0.8); border: 1px solid var(--color-border-soft); }
    .mini-stat span { display: block; color: var(--muted); font-size: 12px; font-weight: 700; }
    .mini-stat strong { display: block; font-size: 18px; line-height: 1.2; }
    .evidence-split { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 20px; align-items: start; min-width: 0; }
    .evidence-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .insight-stack { display: grid; gap: 12px; }
    
    .login-visual-panel { position: relative; min-height: 640px; border-radius: 24px; overflow: hidden; border: 1px solid rgba(221,229,240,.78); box-shadow: var(--shadow); background: linear-gradient(135deg, rgba(16,32,51,.28), rgba(59, 130, 246, .16)), var(--login-image, linear-gradient(135deg, #dbeafe, #ecfeff)); background-size: cover; background-position: center; }
    .login-visual-panel::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(16,32,51,.05), rgba(16,32,51,.56)); }
    .login-product-card { display: grid; align-content: center; min-height: 640px; }
    
    details.debug-details { border: 1px solid var(--line); border-radius: var(--radius-card); padding: 14px; background: #fff; overflow: visible; }
    details.debug-details > .detail-box, .detail-box { max-height: 420px; overflow: auto; }
    
    @keyframes phase31b-rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    @media (max-width: 1080px) {
      .page:has(> .nav) { display: block; padding: 16px; }
      .nav { position: relative; top: auto; min-height: auto; margin-bottom: 20px; align-items: flex-start; flex-direction: column; }
      .nav-links { flex-direction: row; flex-wrap: wrap; }
      .two-col, .dashboard-grid, .chart-side-grid, .flow-board, .analysis-layout { grid-template-columns: 1fr; }
      .split-visual, .evidence-split { grid-template-columns: 1fr; }
      .chart-grid, .metric-grid, #metric-grid, #overview { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
      .login-visual-panel, .login-product-card { min-height: auto; }
      table { font-size: 13px; }
      .page, .app-shell { padding: 16px; }
    }
  </style>
"""


def role_label(role: str) -> str:
    return {"admin": "管理员", "teacher": "教师"}.get(role or "", role or "用户")


def status_label(status: str) -> str:
    return {
        "raw": "待复盘",
        "reviewed": "已复盘",
        "archived": "已归档",
        "ok": "正常",
        "ready": "就绪",
        "success": "成功",
        "failed": "失败",
        "missing": "缺失",
        "partial": "部分完整",
        "complete": "完整",
        "inferred": "推断",
        "stale": "可能过期",
        "online": "在线",
        "offline": "离线",
        "unknown": "未知",
    }.get(status or "", status or "未知")


def risk_label(risk: str) -> str:
    return {"high": "高风险", "medium": "中风险", "low": "低风险", "unknown": "未知"}.get(risk or "", risk or "未知")


def data_source_label(source: str) -> str:
    return {"real": "真实数据", "demo": "演示数据", "all": "全部数据"}.get(source or "", source or "未知")


def ingestion_status_label(status: str) -> str:
    return status_label(status)


def video_status_label(status: str) -> str:
    return {"playable": "可播放", "pending": "待接入", "missing": "缺失", "unknown": "未知"}.get(status or "", status or "未知")
