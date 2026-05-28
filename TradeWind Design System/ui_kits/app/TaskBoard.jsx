// TradeWind — Task Board (floor execution + SOP library)
function TaskBoard({ onNav }) {
  const [filter, setFilter] = React.useState("All");
  const filters = ["All", "My Tasks", "Overdue", "This Week"];

  return (
    <div className="main">
      <Topbar right={
        <div className="row" style={{ gap: 6 }}>
          {filters.map((f) => (
            <span key={f} onClick={() => setFilter(f)}
                  style={{ fontSize: 12.5, fontWeight: 500, padding: "6px 12px", borderRadius: 9999, cursor: "pointer",
                           background: filter === f ? (f === "Overdue" ? "var(--red-bg)" : "var(--emerald-50)") : "transparent",
                           color: filter === f ? (f === "Overdue" ? "var(--red-text)" : "var(--emerald-600)") : (f === "Overdue" ? "var(--red-text)" : "var(--fg2)") }}>
              {f}
            </span>
          ))}
        </div>
      }>
        <div className="title">Task Board</div>
      </Topbar>

      <div className="content split">
        <div style={{ flex: 1, overflowY: "auto", padding: "22px 24px" }}>
          {/* KPI strip */}
          <div className="kpi-strip" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 18 }}>
            <Card className="kpi"><div className="lbl">Active orders</div><div className="num">4</div><div className="sub">3 on track · 1 at risk</div></Card>
            <Card className="kpi"><div className="lbl">Tasks due today</div><div className="num amber">7</div><div className="sub">3 completed · 4 remaining</div></Card>
            <Card className="kpi alert-left"><div className="lbl">Blocked tasks</div><div className="num red">2</div><div className="sub">Waiting on external docs</div></Card>
          </div>

          {/* order cards */}
          <Card className="order-card">
            <div className="oc-head">
              <span className="so">SO-089</span><span className="buyer">Al Barakah Trading · UAE</span>
              <Badge kind="green" icon="circle-check">On Track</Badge>
              <span className="right">Container: Jan 14 · 8 days</span>
            </div>
            <div style={{ padding: "12px 18px 0" }}>
              <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}><span className="muted">6/9 tasks done</span><span className="muted">67%</span></div>
              <Track pct={67} color="emerald" />
            </div>
            <div className="task-list">
              <Task done label="Order received & structured" meta="Jan 3 · auto" />
              <Task done label="Quote sent to buyer" meta="Jan 4 · Rahul" />
              <Task done label="Quote accepted — SO raised" meta="Jan 6 · auto" />
              <Task done label="Vendor PO sent — Ramesh Agro" meta="Jan 7 · Priya" />
              <Task done label="Packaging material ordered" meta="Jan 7 · Priya" />
              <Task done label="Kosher cert attached to order" meta="Jan 8 · Priya" />
              <Task label="Packing floor briefed" pill={["In Progress", "amber"]} who={["S", "#0ea5e9"]} meta="due Jan 10" />
              <Task label="Packing complete & weighed" meta="due Jan 12" />
              <Task label="Container loaded & sealed" meta="due Jan 14" />
            </div>
            <div className="row" style={{ padding: "0 18px 14px", gap: 16 }}>
              <span className="link-accent" style={{ color: "var(--fg3)" }}><i className="ti ti-plus"></i>Add Task</span>
              <span className="link-accent"><i className="ti ti-book"></i>SOP: Kosher Export</span>
            </div>
          </Card>

          <Card className="order-card at-risk">
            <div className="oc-head">
              <span className="so">SO-090</span><span className="buyer">Euro Spices GmbH · Germany</span>
              <Badge kind="amber" icon="alert-triangle">At Risk</Badge>
              <span className="right">Container: Jan 20 · 14 days</span>
            </div>
            <div style={{ padding: "12px 18px 0" }}>
              <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}><span className="muted">3/8 tasks done</span><span className="muted">37%</span></div>
              <Track pct={37} color="amber" />
            </div>
            <div style={{ padding: "12px 18px 0" }}>
              <Alert kind="amber">Sourcing is <b>2.4× slower</b> than usual for this order. At current pace, packing won't start until Jan 16 — only 4 days before container.</Alert>
            </div>
            <div className="task-list">
              <Task done label="Order received" meta="Jan 5 · auto" />
              <Task done label="Quote accepted — SO raised" meta="Jan 7 · auto" />
              <Task done label="Vendor PO sent" meta="Jan 8 · Priya" />
              <Task over label="Raw material received" pill={["Overdue", "red"]} who={["S", "#8b5cf6"]} meta="was due Jan 10" />
              <Task label="Packaging material received" meta="due Jan 12" />
              <Task label="Packing floor briefed" meta="due Jan 14" />
              <Task label="Packing complete" meta="due Jan 17" />
              <Task label="Container loaded" meta="due Jan 20" />
            </div>
          </Card>

          <Card className="order-card">
            <div className="oc-head">
              <span className="so">SO-091</span><span className="buyer">Saffron House UK · United Kingdom</span>
              <Badge kind="slate">Quote Sent</Badge>
              <span className="right">Container: Jan 28 · 22 days</span>
            </div>
            <div style={{ padding: "12px 18px 0" }}>
              <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}><span className="muted">2/8 tasks done</span><span className="muted">25%</span></div>
              <Track pct={25} color="slate" />
            </div>
            <div className="task-list">
              <Task done label="Order received & structured" meta="Jan 6 · auto" />
              <Task done label="Quote sent" meta="Jan 7 · Rahul" />
              <Task label="Awaiting buyer confirmation" meta="due Jan 10" />
              <Task locked label="Vendor PO — unlocks on SO creation" />
              <Task locked label="Packaging material ordered" />
              <Task locked label="Packing floor briefed" />
            </div>
          </Card>
        </div>

        {/* SOP library */}
        <div className="sop-panel">
          <div className="row" style={{ gap: 8, marginBottom: 14 }}><i className="ti ti-book" style={{ fontSize: 18, color: "var(--fg2)" }}></i><span style={{ fontWeight: 600, fontSize: 14 }}>SOP Library</span></div>
          <div className="sop-card"><div className="t">Kosher Export Protocol</div><div className="s">7 steps</div><div style={{ marginTop: 8 }}><Badge kind="emerald">Active on SO-089</Badge></div></div>
          <div className="sop-card"><div className="t">EU Labelling Requirements</div><div className="s">5 steps</div><div style={{ marginTop: 8 }}><Badge kind="emerald">Active on SO-091</Badge></div></div>
          <div className="sop-card" style={{ opacity: .6 }}><div className="t">Halal Certification Workflow</div><div className="s">6 steps</div></div>
          <div className="sop-card" style={{ opacity: .6 }}><div className="t">FSSAI Documentation</div><div className="s">4 steps</div></div>
          <Btn variant="outline" block sm icon="plus">Create SOP</Btn>
        </div>
      </div>
    </div>
  );
}

function Task({ done, over, locked, label, meta, pill, who }) {
  const cls = ["task"];
  if (done) cls.push("done");
  if (over) cls.push("over");
  if (locked) cls.push("locked");
  const icon = done ? "circle-check-filled" : over ? "clock" : "circle";
  return (
    <div className={cls.join(" ")}>
      <i className={"ti ti-" + icon + " check"} style={!done && !over ? { color: "var(--slate-300)" } : {}}></i>
      <span className="label">{label}</span>
      {pill && <span className={"pill " + (pill[1] === "amber" ? "pill-amber" : "pill-red")}>{pill[0]}</span>}
      {who && <Avatar sm initial={who[0]} color={who[1]} />}
      {meta && <span className="meta">{meta}</span>}
    </div>
  );
}

Object.assign(window, { TaskBoard });
