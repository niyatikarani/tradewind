// TradeWind UI kit — shared primitives + app shell. Exported to window.
const { useState } = React;

/* ---------------- primitives ---------------- */
function Badge({ kind = "slate", icon, children }) {
  return (
    <span className={"badge badge-" + kind}>
      {icon && <i className={"ti ti-" + icon}></i>}
      {children}
    </span>
  );
}

function Btn({ variant = "outline", icon, children, block, sm, disabled, onClick }) {
  const cls = ["btn", "btn-" + variant];
  if (block) cls.push("btn-block");
  if (sm) cls.push("btn-sm");
  return (
    <button className={cls.join(" ")} disabled={disabled} onClick={onClick}>
      {icon && <i className={"ti ti-" + icon}></i>}
      {children}
    </button>
  );
}

function Avatar({ initial, color, sm }) {
  return (
    <span className={"avatar" + (sm ? " avatar-sm" : "")} style={{ background: color }}>{initial}</span>
  );
}

function Card({ children, className = "", style }) {
  return <div className={"card " + className} style={style}>{children}</div>;
}

function CardHead({ icon, title, right }) {
  return (
    <div className="card-head">
      <h3>{icon && <i className={"ti ti-" + icon}></i>}{title}</h3>
      {right}
    </div>
  );
}

function Track({ pct, color = "emerald" }) {
  return (
    <div className="track"><div className={"fill fill-" + color} style={{ width: pct + "%" }}></div></div>
  );
}

function Alert({ kind = "amber", icon, children, actions }) {
  return (
    <div className={"alert alert-" + kind}>
      <i className={"ti ti-" + (icon || (kind === "red" ? "alert-circle" : "alert-triangle")) + " lead"}></i>
      <div className="body">{children}</div>
      {actions && <div className="acts">{actions}</div>}
    </div>
  );
}

/* ---------------- app shell ---------------- */
const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "layout-dashboard" },
  { id: "orders", label: "Orders", icon: "file-invoice" },
  { id: "intake", label: "AI Intake", icon: "brain" },
  { id: "quotes", label: "Quotes", icon: "file-text" },
  { id: "tasks", label: "Tasks", icon: "checklist" },
  { id: "analytics", label: "Analytics", icon: "chart-bar" },
  { id: "rules", label: "Rule Engine", icon: "settings" },
];

function Sidebar({ active, onNav }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <img src="../../assets/logomark.svg" alt="TradeWind" />
        <span className="word">Trade<b>Wind</b></span>
      </div>
      <nav className="nav">
        {NAV.map((n) => (
          <div key={n.id}
               className={"nav-item" + (active === n.id ? " active" : "")}
               onClick={() => onNav && onNav(n.id)}>
            <i className={"ti ti-" + n.icon}></i>{n.label}
          </div>
        ))}
      </nav>
      <div className="user">
        <Avatar initial="R" color="#059669" />
        <div className="meta">
          <div className="n">Rahul Mehta</div>
          <div className="o">S&amp;G Exports</div>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ children, right }) {
  return (
    <header className="topbar">
      {children}
      <div className="right">{right}</div>
    </header>
  );
}

function NotifBell({ count }) {
  return (
    <div className="notif"><i className="ti ti-bell" style={{ fontSize: 20 }}></i>{count ? <span className="dot">{count}</span> : null}</div>
  );
}

Object.assign(window, { Badge, Btn, Avatar, Card, CardHead, Track, Alert, Sidebar, Topbar, NotifBell, NAV });
