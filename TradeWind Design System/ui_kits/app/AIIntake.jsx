// TradeWind — AI Order Intake (chat + extracted data)
function AIIntake({ onNav }) {
  return (
    <div className="main">
      <Topbar right={<Badge kind="amber" icon="clock">3 pending review</Badge>}>
        <div className="title">AI Order Intake</div>
      </Topbar>
      <div className="content split">
        <div className="intake">
          {/* LEFT — chat */}
          <div className="chat-col">
            <div className="chat-head">
              <div style={{ fontSize: 14, fontWeight: 600 }}>New Intake</div>
              <div className="select"><i className="ti ti-paperclip" style={{ fontSize: 14 }}></i>Paste text / image URL / forward<i className="ti ti-chevron-down" style={{ fontSize: 14 }}></i></div>
            </div>
            <div className="chat-thread">
              <div className="bubble system">Drop an order here. Paste a WhatsApp message, type it out, or paste an image URL. I'll extract the details.</div>

              <div className="bubble user">Al Barakah wants 500kg cinnamon sticks, kosher, delivery by 14th Jan, FOB Mundra. Also 200kg cardamom bold. Payment 30 days LC.</div>

              {/* AI executes actions on your behalf */}
              <div className="bubble ai">
                <div className="ai-head"><i className="ti ti-sparkles"></i>TradeWind AI</div>
                On it — structuring this into a sales order.
                <div className="run">
                  <div className="run-head"><i className="ti ti-bolt"></i>Actions<span className="count">3 done · 1 running</span></div>
                  <div className="act"><i className="ti ti-check" style={{ color: "var(--green-text)" }}></i><span className="lbl">Matched SKUs to catalogue</span><span className="res">2 of 2</span></div>
                  <div className="act"><i className="ti ti-check" style={{ color: "var(--green-text)" }}></i><span className="lbl">Identified buyer</span><span className="res">Al Barakah Trading</span></div>
                  <div className="act"><i className="ti ti-check" style={{ color: "var(--green-text)" }}></i><span className="lbl">Locked FX rate</span><span className="res mono">₹83.4/$</span></div>
                  <div className="act running"><span className="spin"></span><span className="lbl">Drafting sales order…</span><span className="res mono">SO-089</span></div>
                </div>
              </div>

              {/* AI asks a clarifying question */}
              <div className="bubble ai">
                <div className="ai-head"><i className="ti ti-sparkles"></i>TradeWind AI</div>
                "Cardamom bold" matched 3 SKUs — which did you mean?
                <div className="ask">
                  <span className="q-lbl"><i className="ti ti-help-circle" style={{ fontSize: 13 }}></i>Needs your input</span>
                  <div className="q">Pick the right cardamom SKU:</div>
                  <div className="opts">
                    <div className="opt"><span className="k">CARD-BOLD-7MM</span><span className="d">Green Cardamom Bold 7mm</span><span className="rec">Best match</span></div>
                    <div className="opt"><span className="k">CARD-STD-5MM</span><span className="d">Cardamom Standard 5mm</span></div>
                    <div className="opt"><span className="k">CARD-GRN-A</span><span className="d">Green Cardamom Grade A</span></div>
                  </div>
                </div>
              </div>

              <div className="bubble user">It's the 7mm — CARD-BOLD-7MM. And delivery is 14th Jan CIF, not FOB.</div>

              <div className="bubble ai">
                <div className="ai-head"><i className="ti ti-sparkles"></i>TradeWind AI</div>
                Updated. Set cardamom to <span className="mono">CARD-BOLD-7MM</span> and Incoterm to CIF Mundra. CIF means freight and insurance are your cost — I've reflected that in the draft quote. Ready to confirm?
                <div className="btn-row">
                  <Btn variant="primary" icon="circle-check" onClick={() => onNav("order")}>Confirm &amp; Create SO</Btn>
                  <Btn variant="outline">Assign to Rahul</Btn>
                </div>
              </div>
            </div>
            <div className="composer">
              <div className="box">
                <input placeholder="Paste order text, describe an order, or ask anything..." />
                <button className="icon-btn attach"><i className="ti ti-paperclip"></i></button>
                <button className="icon-btn send"><i className="ti ti-send"></i></button>
              </div>
              <div className="note">Supports WhatsApp text, voice note transcripts, email forwards, PDF text</div>
            </div>
          </div>

          {/* RIGHT — extracted */}
          <div className="extract-col">
            <div className="row" style={{ justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{ fontSize: 15, fontWeight: 600 }}>Extracted Order</div>
              <Badge kind="amber" icon="clock">Draft — pending confirm</Badge>
            </div>

            <div className="section-label">Buyer</div>
            <Card className="card-pad">
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>Al Barakah Trading · UAE</div>
                  <div className="muted" style={{ marginTop: 2 }}>LC 30 days · Last order Nov 2024 · 3 orders total</div>
                </div>
                <Badge kind="green" icon="circle-check">Known buyer</Badge>
              </div>
            </Card>

            <div className="section-label">Line Items</div>
            <Card>
              <table className="tw">
                <thead><tr><th>SKU</th><th>Description</th><th>Qty</th><th>Incoterm</th><th>Cert</th><th>Conf.</th></tr></thead>
                <tbody>
                  <tr>
                    <td className="mono" style={{ fontSize: 11.5 }}>CINN-STICKS-001</td>
                    <td>Cinnamon Sticks</td><td>500 kg</td><td>CIF</td>
                    <td><Badge kind="emerald">Kosher</Badge></td>
                    <td><Badge kind="green">96%</Badge></td>
                  </tr>
                  <tr>
                    <td className="mono" style={{ fontSize: 11.5 }}>CARD-BOLD-7MM</td>
                    <td>Green Cardamom Bold 7mm</td><td>200 kg</td><td>CIF</td>
                    <td style={{ color: "var(--fg3)" }}>—</td>
                    <td><Badge kind="amber">81%</Badge></td>
                  </tr>
                </tbody>
              </table>
            </Card>
            <div style={{ marginTop: 10 }}>
              <Alert kind="amber" actions={<Btn variant="outline" sm>Pick SKU</Btn>}>
                <span className="mono">CARD-BOLD-7MM</span> has 3 similar SKUs — confirm this is the right one before creating SO.
              </Alert>
            </div>

            <div className="section-label">Order Meta</div>
            <Card className="card-pad">
              <div className="kv"><span className="k">Delivery</span><span className="v">14 Jan 2025 · 22 days away</span></div>
              <div className="kv"><span className="k">Port</span><span className="v">Mundra (CIF)</span></div>
              <div className="kv"><span className="k">Payment</span><span className="v">LC 30 days</span></div>
              <div className="kv"><span className="k">Container</span><span className="v">Est. 20ft FCL · 62% util.</span></div>
            </Card>

            <div className="section-label">Actions</div>
            <div className="stack" style={{ gap: 9 }}>
              <Btn variant="primary" block icon="circle-check" onClick={() => onNav("order")}>Create Sales Order</Btn>
              <Btn variant="outline" block>Save as Draft</Btn>
            </div>
            <div className="muted" style={{ marginTop: 10, textAlign: "center" }}>AI extracted from 2 messages · 3 fields confirmed by user · 1 pending</div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { AIIntake });
