// TradeWind — Dashboard (manager control room)
function Dashboard({ onNav }) {
  const orders = [
    { so: "SO-089", buyer: "Al Barakah · UAE", stage: "Packing", value: "₹14.8L", margin: "12.4%", deadline: "Jan 14 · 8d", dl: "amber", status: ["On Track", "green"] },
    { so: "SO-090", buyer: "Euro Spices · DE", stage: "Sourcing", value: "₹8.2L", margin: "11.8%", deadline: "Jan 20 · 14d", dl: "green", status: ["At Risk", "amber"] },
    { so: "SO-091", buyer: "Saffron House · UK", stage: "Quote Sent", value: "₹6.1L", margin: "—", deadline: "Jan 28 · 22d", dl: "green", status: ["Pending", "slate"] },
    { so: "SO-088", buyer: "Gulf Traders · KW", stage: "Shipped", value: "₹22.4L", margin: "13.1%", deadline: "Shipped ✓", dl: "muted", status: ["Shipped", "green"] },
    { so: "SO-087", buyer: "Herb Direct · NL", stage: "Completed", value: "₹11.0L", margin: "14.2%", deadline: "Done ✓", dl: "muted", status: ["Done", "slate"] },
  ];
  const dlColor = { amber: "var(--amber-text)", green: "var(--green-text)", red: "var(--red-text)", muted: "var(--fg3)" };

  const tasks = [
    { pill: ["In Progress", "amber"], t: "Brief packing floor", so: "SO-089", who: "Suresh", due: "Due today" },
    { pill: ["Overdue", "red"], t: "Confirm raw material receipt", so: "SO-090", who: "Priya", due: "Was due Jan 10" },
    { pill: ["Pending", "slate"], t: "Upload COA document", so: "SO-089", who: "Priya", due: "Due today" },
    { pill: ["Pending", "slate"], t: "Send revised quote v2", so: "SO-091", who: "Rahul", due: "Due today" },
  ];
  const pillCls = { amber: "pill-amber", red: "pill-red", slate: "badge-slate" };

  return (
    <div className="main">
      <Topbar right={<><span style={{ fontSize: 13, color: "var(--fg2)" }}>Good morning, <b style={{ color: "var(--fg1)" }}>Rahul</b> · S&amp;G Exports</span><NotifBell count={2} /></>}>
        <div className="title">Dashboard</div>
      </Topbar>
      <div className="content">
        {/* KPI strip */}
        <div className="kpi-strip" style={{ gridTemplateColumns: "repeat(5, 1fr)" }}>
          <Card className="kpi"><div className="lbl">Orders this month</div><div className="num accent">14</div><div className="sub">↑ 3 vs last month</div></Card>
          <Card className="kpi"><div className="lbl">Open quotes</div><div className="num accent">₹42L</div><div className="sub">3 awaiting buyer reply</div></Card>
          <Card className="kpi"><div className="lbl">Avg. margin</div><div className="num">12.4%</div><div className="sub">↑ 1.2pp vs last quarter</div></Card>
          <Card className="kpi"><div className="lbl">Container util.</div><div className="num green">87%</div><div className="sub">across active FCLs</div></Card>
          <Card className="kpi alert-left"><div className="lbl">Overdue tasks</div><div className="num red">2</div><div className="sub">needs attention</div></Card>
        </div>

        {/* alerts */}
        <div className="stack" style={{ marginTop: 16 }}>
          <Alert kind="red" actions={<Btn variant="outline" sm onClick={() => onNav("order")}>View Order</Btn>}>
            <b>SO-090 — Raw material delivery is 2 days overdue.</b> Container date Jan 20 is now at risk.
          </Alert>
          <Alert kind="amber" actions={<><Btn variant="outline" sm>Contact Buyer</Btn><Btn variant="ghost" sm>Dismiss</Btn></>}>
            <b>SO-089 —</b> Container utilisation 67%, below your 85% threshold. 58 cartons of space unused.
          </Alert>
        </div>

        {/* main grid */}
        <div className="grid-65-35" style={{ marginTop: 16 }}>
          <div className="stack">
            <Card>
              <CardHead title="Active Orders (5)" right={<Btn variant="primary" sm icon="plus" onClick={() => onNav("intake")}>New Order</Btn>} />
              <table className="tw">
                <thead><tr><th>Order</th><th>Buyer</th><th>Stage</th><th>Value</th><th>Margin</th><th>Deadline</th><th>Status</th></tr></thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.so} className="clickable" onClick={() => onNav("order")}>
                      <td className="mono" style={{ fontWeight: 600 }}>{o.so}</td>
                      <td>{o.buyer}</td>
                      <td style={{ color: "var(--fg2)" }}>{o.stage}</td>
                      <td>{o.value}</td>
                      <td>{o.margin}</td>
                      <td style={{ color: dlColor[o.dl], fontWeight: 500 }}>{o.deadline}</td>
                      <td><Badge kind={o.status[1]}>{o.status[0]}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            <Card>
              <CardHead title="Tasks Due Today" right={<Badge kind="slate">4 remaining / 7 total</Badge>} />
              <div style={{ padding: "6px 18px 14px" }}>
                {tasks.map((t, i) => (
                  <div key={i} className="row" style={{ padding: "9px 0", borderBottom: i < tasks.length - 1 ? "1px solid var(--border)" : "none" }}>
                    <span className={"task-pill " + (t.pill[1] === "slate" ? "badge badge-slate" : "")}
                          style={t.pill[1] !== "slate" ? { fontSize: 10.5, fontWeight: 600, borderRadius: 6, padding: "3px 8px", background: t.pill[1] === "amber" ? "var(--amber-bg)" : "var(--red-bg)", color: t.pill[1] === "amber" ? "var(--amber-text)" : "var(--red-text)" } : {}}>
                      {t.pill[0]}
                    </span>
                    <span style={{ fontSize: 13, color: "var(--fg1)", flex: 1 }}>{t.t}</span>
                    <span className="mono muted">{t.so}</span>
                    <span className="muted">· {t.who} · {t.due}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* right rail */}
          <div className="stack">
            <Card>
              <CardHead icon="calendar" title="Upcoming Deadlines" />
              <div style={{ padding: "10px 18px 16px" }}>
                <DeadlineDay label="Jan 10 (Today)" items={[["Packing floor briefed — SO-089", "amber"], ["Upload COA — SO-089", "amber"]]} />
                <DeadlineDay label="Jan 12" items={[["Packing complete & weighed — SO-089", "green"]]} />
                <DeadlineDay label="Jan 14 ← Container date" items={[["Container loaded — SO-089", "red"]]} crit />
                <DeadlineDay label="Jan 20 ← Container date" items={[["Container loaded — SO-090", "amber"]]} last />
              </div>
            </Card>

            <Card className="card-pad">
              <div className="row" style={{ gap: 8, marginBottom: 10 }}>
                <i className="ti ti-sparkles" style={{ color: "var(--emerald-600)", fontSize: 17 }}></i>
                <span style={{ fontWeight: 600, fontSize: 14 }}>Ask TradeWind anything</span>
              </div>
              <div className="composer" style={{ padding: 0, border: "none" }}>
                <div className="box">
                  <input placeholder="What's the margin on SO-089? / Which orders have stale prices?" />
                  <button className="icon-btn send"><i className="ti ti-send"></i></button>
                </div>
              </div>
              <div className="suggest-row">
                <span className="suggest">Show at-risk orders</span>
                <span className="suggest">Stale vendor prices</span>
                <span className="suggest">This week's deadlines</span>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function DeadlineDay({ label, items, crit, last }) {
  const dot = { amber: "var(--amber-text)", green: "var(--green-text)", red: "var(--red-text)" };
  return (
    <div style={{ marginBottom: last ? 0 : 14 }}>
      <div style={{ fontSize: 11.5, fontWeight: 600, color: crit ? "var(--red-text)" : "var(--fg2)", marginBottom: 6 }}>{label}</div>
      {items.map((it, i) => (
        <div key={i} className="row" style={{ gap: 8, padding: "3px 0" }}>
          <span style={{ width: 7, height: 7, borderRadius: 9999, background: dot[it[1]], flexShrink: 0 }}></span>
          <span style={{ fontSize: 12.5, color: "var(--fg1)" }}>{it[0]}</span>
        </div>
      ))}
    </div>
  );
}

Object.assign(window, { Dashboard });
