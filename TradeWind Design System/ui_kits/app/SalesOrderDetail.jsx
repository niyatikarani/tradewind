// TradeWind — Sales Order Detail (timeline + warnings + documents)
function SalesOrderDetail({ onNav }) {
  return (
    <div className="main">
      <Topbar right={<><Btn variant="outline" sm icon="edit">Edit</Btn><Btn variant="outline" sm icon="printer">Print Packing List</Btn><Btn variant="primary" sm icon="download">Download PDF</Btn></>}>
        <div className="crumb">Orders / <b>SO-2024-089</b></div>
      </Topbar>
      <div className="content">
        {/* header card */}
        <Card className="card-pad">
          <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
            <div>
              <div className="mono" style={{ fontSize: 20, fontWeight: 700 }}>SO-2024-089</div>
              <div style={{ color: "var(--fg2)", fontSize: 13, marginTop: 3 }}>Al Barakah Trading · UAE</div>
              <div className="row" style={{ gap: 7, marginTop: 10, flexWrap: "wrap" }}>
                <Badge kind="green" icon="circle-check">Confirmed</Badge>
                <Badge kind="amber" icon="package">Packing in Progress</Badge>
                <Badge kind="emerald">Kosher</Badge>
                <Badge kind="slate">CIF Mundra</Badge>
              </div>
            </div>
            <div className="kpi-strip" style={{ gridTemplateColumns: "repeat(4, max-content)", gap: 26 }}>
              <div><div className="lbl" style={{ fontSize: 10.5 }}>Total value</div><div style={{ fontSize: 19, fontWeight: 700, marginTop: 4 }}>₹14,82,000</div></div>
              <div><div className="lbl" style={{ fontSize: 10.5 }}>Margin</div><div style={{ fontSize: 19, fontWeight: 700, marginTop: 4, color: "var(--emerald-600)" }}>12.4%</div></div>
              <div><div className="lbl" style={{ fontSize: 10.5 }}>Container</div><div style={{ fontSize: 19, fontWeight: 700, marginTop: 4, color: "var(--amber-text)" }}>67% full</div></div>
              <div><div className="lbl" style={{ fontSize: 10.5 }}>Deadline</div><div style={{ fontSize: 19, fontWeight: 700, marginTop: 4, color: "var(--green-text)" }}>Jan 14 · 8d</div></div>
            </div>
          </div>
        </Card>

        {/* alert banners */}
        <div className="stack" style={{ marginTop: 16 }}>
          <Alert kind="amber" actions={<><Btn variant="outline" sm>Contact Buyer</Btn><Btn variant="outline" sm>Switch Container</Btn></>}>
            Container utilisation is <b>67%</b> — below your 85% threshold. 58 more cartons fit. Consider adding volume or switching to a 10ft container.
          </Alert>
          <Alert kind="amber">
            Packing stage is running <b>1.8× longer</b> than the average for this buyer. Container loading is Jan 14 — 8 days away.
          </Alert>
        </div>

        {/* 60/40 */}
        <div className="grid-60-40" style={{ marginTop: 16 }}>
          {/* LEFT */}
          <div className="stack">
            <Card>
              <CardHead title="Order Items" right={<Badge kind="slate">2 SKUs</Badge>} />
              <table className="tw">
                <thead><tr><th>SKU</th><th>Description</th><th>Qty</th><th>Unit Price</th><th>Pack Format</th><th>Cert</th><th style={{ textAlign: "right" }}>Line Total</th></tr></thead>
                <tbody>
                  <tr>
                    <td className="mono" style={{ fontSize: 11.5 }}>CINN-STICKS-001</td><td>Cinnamon Sticks</td><td>500 kg</td><td>₹296/kg</td><td className="muted">100g kraft · 24/ctn</td><td><Badge kind="emerald">Kosher</Badge></td><td style={{ textAlign: "right" }}>₹1,48,000</td>
                  </tr>
                  <tr>
                    <td className="mono" style={{ fontSize: 11.5 }}>CARD-BOLD-7MM</td><td>Green Cardamom Bold 7mm</td><td>200 kg</td><td>₹542/kg</td><td className="muted">50g pouch · 48/ctn</td><td style={{ color: "var(--fg3)" }}>—</td><td style={{ textAlign: "right" }}>₹1,08,400</td>
                  </tr>
                </tbody>
                <tfoot><tr><td colSpan="6">Total</td><td style={{ textAlign: "right" }}>₹14,82,000</td></tr></tfoot>
              </table>
              <div className="muted" style={{ padding: "10px 14px" }}>Prices include packaging cost · FX locked at ₹83.4/$ on Jan 3 11:30 IST · RBI FBIL</div>
            </Card>

            <Card>
              <CardHead title="Packaging Config" />
              <div className="card-pad" style={{ paddingTop: 12 }}>
                <div className="kv"><span className="k">Container</span><span className="v">20ft FCL</span></div>
                <div className="kv"><span className="k">Total cartons</span><span className="v">480</span></div>
                <div style={{ padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                  <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}><span className="k" style={{ fontSize: 13, color: "var(--fg2)" }}>CBM utilisation</span><span style={{ fontSize: 12 }} className="mono">16.8 / 25.0 m³</span></div>
                  <Track pct={67} color="amber" />
                </div>
                <div className="kv"><span className="k">Weight</span><span className="v">1,152 kg / 22,000 kg max</span></div>
                <div className="row" style={{ gap: 8, marginTop: 12, flexWrap: "wrap" }}>
                  <Badge kind="green" icon="circle-check">Kosher: no chemical treatment</Badge>
                  <Badge kind="red" icon="lock">Steam pasteurisation restricted</Badge>
                  <Badge kind="amber" icon="alert-triangle">COA required before shipment</Badge>
                </div>
              </div>
            </Card>

            <Card>
              <CardHead title="Required Documents" right={<Badge kind="amber">4/6 ready</Badge>} />
              <div style={{ padding: "8px 18px 14px" }}>
                <DocRow ok label="Commercial Invoice" note="auto-generated" />
                <DocRow ok label="Packing List" note="auto-generated" />
                <DocRow ok label="Kosher Certificate" note="attached Jan 8" />
                <DocRow ok label="FSSAI Lab Report" note="attached Jan 9" />
                <DocRow label="Certificate of Origin" note="pending" />
                <DocRow label="Phytosanitary Certificate" note="pending" last />
                <Btn variant="outline" sm icon="upload" >Upload Document</Btn>
              </div>
            </Card>
          </div>

          {/* RIGHT */}
          <div className="stack">
            <Card>
              <CardHead title="Order Timeline" />
              <div className="card-pad">
                <div className="timeline">
                  <TL icon="package" color="var(--amber-text)" title="Packing in progress" meta="Jan 9, 2:30 PM · Suresh" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="FSSAI cert attached" meta="Jan 9, 10:45 AM · Priya" />
                  <TL dashed icon="alert-triangle" color="var(--amber-text)" title="Packing delayed 2 days" meta="Jan 9, 10:45 AM · system" note="FSSAI certificate arrived late. Packing restarted immediately." />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Packaging PO sent" meta="Jan 7, 3:00 PM · Priya" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Raw material PO sent" meta="Jan 7, 2:45 PM · Priya" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="SO created" meta="Jan 6, 11:20 AM · auto on quote accept" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Quote accepted by buyer" meta="Jan 6, 11:18 AM" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Quote sent" meta="Jan 4, 4:30 PM · Rahul" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Order structured by AI" meta="Jan 3, 9:16 AM · 2 min from intake" />
                  <TL icon="circle-check-filled" color="var(--green-text)" title="Order received (WhatsApp)" meta="Jan 3, 9:14 AM · Al Barakah" last />
                </div>
              </div>
            </Card>

            <Card className="card-pad" style={{ borderLeft: "3px solid var(--emerald-500)" }}>
              <div className="row" style={{ gap: 7, marginBottom: 7 }}><i className="ti ti-sparkles" style={{ color: "var(--emerald-600)", fontSize: 16 }}></i><span style={{ fontWeight: 600, fontSize: 13 }}>AI Summary</span></div>
              <div style={{ fontSize: 13, lineHeight: 1.55, color: "var(--fg1)" }}>Received Jan 3 via WhatsApp. Quoted Jan 4, accepted Jan 6. Packing delayed 2 days on Jan 9 — FSSAI certificate arrived late. Resumed immediately. On track for Jan 14 container loading. No compliance issues.</div>
            </Card>

            <Card className="card-pad">
              <div className="composer" style={{ padding: 0, border: "none" }}>
                <div className="box"><input placeholder="Ask anything about this order..." /><button className="icon-btn send"><i className="ti ti-send"></i></button></div>
              </div>
              <div style={{ marginTop: 12, fontSize: 13 }}>
                <div style={{ color: "var(--fg2)", fontWeight: 500 }}>Q: Why was packing delayed?</div>
                <div style={{ marginTop: 4, color: "var(--fg1)", lineHeight: 1.5 }}>→ FSSAI lab report was received on Jan 9 instead of Jan 7. Priya uploaded it immediately and packing resumed the same day.</div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function DocRow({ ok, label, note, last }) {
  return (
    <div className="row" style={{ padding: "8px 0", borderBottom: last ? "1px solid var(--border)" : "1px solid var(--border)", marginBottom: last ? 12 : 0, gap: 9 }}>
      <i className={"ti ti-" + (ok ? "circle-check-filled" : "alert-triangle")} style={{ fontSize: 17, color: ok ? "var(--green-text)" : "var(--amber-text)" }}></i>
      <span style={{ fontSize: 13, flex: 1, color: "var(--fg1)" }}>{label}</span>
      <span className="muted">{note}</span>
    </div>
  );
}

function TL({ icon, color, title, meta, note, dashed, last }) {
  return (
    <div className={"tl-item" + (dashed ? " dashed" : "")}>
      <span className="tl-dot"><i className={"ti ti-" + icon} style={{ color }}></i></span>
      <div className="tl-title">{title}</div>
      <div className="tl-meta">{meta}</div>
      {note && <div className="tl-note">{note}</div>}
    </div>
  );
}

Object.assign(window, { SalesOrderDetail });
