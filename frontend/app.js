// =====================
// Utilities & Theming
// =====================
const ACCENT = "#22C55E"; // cyber green

// JSON -> <pre> (debug only)
function setOut(id, data) {
  const el = document.getElementById(id);
  if (!el) return;
  try { el.textContent = JSON.stringify(data, null, 2); }
  catch { el.textContent = String(data); }
}

// Toast notifications
function notify(msg, type = "info") {
  const host = document.getElementById("toasts");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<div class="dot"></div><div class="msg">${msg}</div>`;
  host.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  setTimeout(() => { el.classList.remove("show"); setTimeout(() => el.remove(), 300); }, 3200);
}

// fetch wrapper with safe JSON & toast on error
async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(url, options);
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text; }
    if (!res.ok) {
      console.error("API Error:", url, res.status, data);
      notify(`${data?.detail || data?.error || text}`, "error");
      throw new Error(data?.detail || text);
    }
    return data;
  } catch (err) {
    notify(`Network error: ${err.message}`, "error");
    throw err;
  }
}

// footer session label
function updateFootSession() {
  const sid = localStorage.getItem("session_id");
  document.getElementById("footSession").textContent = `Session: ${sid || "—"}`;
}

// ============
// Role toggle
// ============
function setRole(role) {
  localStorage.setItem("role", role);
  document.getElementById("roleConsumer").classList.toggle("active", role === "consumer");
  document.getElementById("roleProducer").classList.toggle("active", role === "producer");
  document.querySelector(".role-consumer-only").classList.toggle("hidden", role !== "consumer");
  document.querySelector(".role-producer-only").classList.toggle("hidden", role !== "producer");
}
function initRole() {
  const saved = localStorage.getItem("role") || "consumer";
  setRole(saved);
  document.getElementById("roleConsumer").addEventListener("click", () => setRole("consumer"));
  document.getElementById("roleProducer").addEventListener("click", () => setRole("producer"));
}

// ==========================
// Wizard tabs & progression
// ==========================
const tabs = ["tab-auth","tab-workspace","tab-negotiation","tab-summary"];
function setTab(tabId) {
  for (const id of tabs) document.getElementById(id).classList.toggle("active", id === tabId);
  document.querySelectorAll(".wizard .tab").forEach(btn => btn.classList.toggle("active", btn.dataset.tab === tabId));
  const idx = tabs.indexOf(tabId), pct = ((idx+1)/tabs.length)*100;
  document.getElementById("progressBar").style.width = `${pct}%`;
}
function initTabs() {
  document.querySelectorAll(".wizard .tab").forEach(btn => btn.addEventListener("click", () => setTab(btn.dataset.tab)));
  setTab("tab-auth");
}

// =====================
// Session / round state
// =====================
function saveSession(sessionId) {
  localStorage.setItem("session_id", sessionId);
  ["session_id","choose_session_id"].forEach(id => { const el = document.getElementById(id); if (el) el.value = sessionId; });
  updateFootSession();
}
function getSession() {
  return localStorage.getItem("session_id") ||
         document.getElementById("session_id")?.value ||
         document.getElementById("choose_session_id")?.value || "";
}
function setCurrentRound(n) {
  localStorage.setItem("current_round", String(n));
  ["round_number","choose_round_number"].forEach(id => { const el = document.getElementById(id); if (el) el.value = n; });
}
function getCurrentRound() { return Number(localStorage.getItem("current_round") || "1"); }

// ===============
// Human renderers
// ===============
function humanRequestView(req) {
  const el = document.getElementById("request_human");
  if (!el) return;
  el.innerHTML = `
    <div class="human-line">Request submitted: <strong>${req.product_name}</strong>, <strong>${req.quantity}</strong> units, budget <strong>$${req.budget}</strong>.</div>
  `;
}
function humanProducerView(prod) {
  const el = document.getElementById("producer_human");
  if (!el) return;
  el.innerHTML = `
    <div class="human-line">Product registered: <strong>${prod.name}</strong> in <strong>${prod.domain}</strong>, price <strong>$${prod.price}</strong>, stock <strong>${prod.quantity}</strong>.</div>
  `;
}
function humanStartView(data) {
  const el = document.getElementById("start_human");
  if (!el) return;

  // rounds: prefer total_rounds, fallback to config/legacy
  const rounds =
    data.total_rounds ??
    data.config?.num_rounds ??
    data.num_rounds ??
    "—";

  // producers: not explicit in your JSON; infer from offers length on start
  const producers =
    data.num_producers ??
    data.total_producers ??
    (Array.isArray(data.offers) ? data.offers.length : undefined) ??
    "—";

  el.innerHTML = `
    <div class="human-line">Negotiation started with <strong>${producers}</strong> producers for <strong>${rounds}</strong> rounds.</div>
    <div class="human-sub">Session ID: <code>${data.session_id || "—"}</code></div>
  `;
}

function humanChooseView(data) {
  const el = document.getElementById("choose_human");
  if (!el) return;
  const status = data?.status || "processed";
  el.innerHTML = `<div class="human-line">Choice saved: <strong>${status}</strong>.</div>`;
}
function humanFinalView(data) {
  const el = document.getElementById("final_human");
  if (!el) return;

  // prefer producer_response.final_terms (final contracted terms); fallback to selected_offer.offer
  const sel = data.selected_offer || {};
  const finalTerms = data.producer_response?.final_terms || sel.offer || {};
  const pid = sel.producer_id ?? sel.producer_name?.match(/\d+/)?.[0] ?? "?" ;

  const price = finalTerms.price ?? "—";
  const qty = finalTerms.quantity ?? "—";
  const del = finalTerms.delivery_terms ?? "N/A";
  const pay = finalTerms.payment_terms ?? "N/A";

  const sat = sel.satisfaction?.total_satisfaction ?? "—";

  el.innerHTML = `
    <div class="human-line">✅ Finalized with <strong>Producer #${pid}</strong>:
      <strong>${qty}</strong> units @ <strong>$${price}/unit</strong>,
      delivery <strong>${del}</strong>, payment <strong>${pay}</strong>.
      ${sat !== "—" ? `Satisfaction: <strong>${sat}%</strong>` : ""}
    </div>
  `;
}

function humanSummaryView(data) {
  const el = document.getElementById("summary_human");
  if (!el) return;

  const fd = data.final_deal || {};
  const t = fd.final_terms || {};
  const pid = fd.producer_id ?? fd.producer_name?.match(/\d+/)?.[0] ?? "?" ;

  const price = t.price ?? "—";
  const qty = t.quantity ?? "—";
  const sat = fd.satisfaction?.total_satisfaction ?? "—";

  el.innerHTML = `
    <div class="human-line">Summary loaded. Best deal: <strong>Producer #${pid}</strong>,
      <strong>${qty}</strong> units @ <strong>$${price}/unit</strong>.
      ${sat !== "—" ? `Satisfaction: <strong>${sat}%</strong>.` : ""}
    </div>
  `;
}


// Round table renderer
function renderOffersTable(roundJson) {
  const wrap = document.getElementById("offers_table_wrap");
  if (!wrap) return;

  const offers = roundJson?.offers || [];
  const roundNo = roundJson?.round ?? roundJson?.round_number ?? getCurrentRound();

  if (!offers.length) {
    wrap.innerHTML = `<div class="empty">No offers available for round ${roundNo}.</div>`;
    return;
  }

  const rows = offers.map((offer, i) => {
    const o = offer.offer || {};
    // satisfaction: object (start) OR flat score (rounds)
    const score = (offer.satisfaction?.total_satisfaction ?? offer.satisfaction_score ?? null);
    const scoreTxt = score != null ? `${Number(score).toFixed(1)}%` : "—";
    let satClass = "sat-mid";
    if (score != null) { if (score >= 75) satClass = "sat-good"; else if (score < 50) satClass = "sat-bad"; }

    return `
      <tr>
        <td>#${offer.producer_id ?? "?"}</td>
        <td>$${o.price ?? "—"}</td>
        <td>${o.quantity ?? "—"}</td>
        <td>${o.delivery_terms ?? "N/A"}</td>
        <td>${o.payment_terms ?? "N/A"}</td>
        <td><span class="${satClass}">${scoreTxt}</span></td>
        <td><button class="primary choose-btn" data-idx="${i+1}">Choose</button></td>
      </tr>
    `;
  }).join("");

  wrap.innerHTML = `
    <div class="round-head">Showing <strong>Round ${roundNo}</strong></div>
    <div class="table-wrap">
      <table class="offers-table">
        <thead>
          <tr>
            <th>Producer</th><th>Price ($/u)</th><th>Qty</th>
            <th>Delivery</th><th>Payment</th><th>Satisfaction</th><th>Action</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;

  // choose buttons
  wrap.querySelectorAll(".choose-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const idx = Number(btn.dataset.idx);
      const body = { round_number: roundNo, offer_index: idx };
      const chooseData = await fetchJSON(`/negotiation/${getSession()}/choose`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
      });
      setOut("choose_out", chooseData);
      humanChooseView(chooseData);
      notify("Offer chosen", "success");
    });
  });
}


// ==================
// Auth: signup/login
// ==================
async function signup() {
  const role = document.getElementById("signup_role").value;
  const body = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    role,
    password: document.getElementById("password").value,
  };
  const data = await fetchJSON("/auth/signup", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
  });
  setOut("signup_out", data);
  if (data.id) {
    localStorage.setItem("user_id", String(data.id));
    if (role === "consumer") {
      localStorage.setItem("consumer_id", String(data.id));
      document.getElementById("consumer_id").value = data.id;
      setRole("consumer");
    } else {
      localStorage.setItem("producer_id", String(data.id));
      document.getElementById("producer_id").value = data.id;
      setRole("producer");
    }
    notify("Signup successful", "success");
    setTab("tab-workspace");
  } else {
    notify("Signup failed or user exists", "warning");
  }
}

async function login() {
  const email = document.getElementById("login_email").value;
  const password = document.getElementById("login_password").value;
  const url = new URL("/auth/login", window.location.origin);
  url.searchParams.set("email", email);
  url.searchParams.set("password", password);
  const data = await fetchJSON(url.toString(), { method: "POST" });
  setOut("login_out", data);
  if (data.id) {
    localStorage.setItem("user_id", String(data.id));
    localStorage.setItem("consumer_id", String(data.id));
    document.getElementById("consumer_id").value = data.id;
    notify("Login successful", "success");
    setTab("tab-workspace");
  } else {
    notify("Invalid credentials", "error");
  }
}

// ==========================
// Consumer: submit request
// ==========================
async function submitRequest() {
  let specs = {};
  try { specs = JSON.parse(document.getElementById("specs").value || "{}"); }
  catch { return notify("Invalid specs JSON", "warning"); }

  const body = {
    consumer_id: Number(document.getElementById("consumer_id").value || localStorage.getItem("consumer_id")),
    product_name: document.getElementById("product_name").value,
    quantity: Number(document.getElementById("quantity").value),
    budget: Number(document.getElementById("budget").value),
    specs,
  };
  const data = await fetchJSON("/requests/submit", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
  });
  setOut("request_out", data);
  humanRequestView(body);
  notify("Request submitted", "success");
  setTab("tab-negotiation");
}

// ==========================
// Producer: register product
// ==========================
async function addProduct() {
  const pid = Number(document.getElementById("producer_id")?.value || localStorage.getItem("producer_id"));
  if (!pid) return notify("Producer ID required. Login as producer.", "warning");

  let specs = {};
  try { specs = JSON.parse(document.getElementById("prod_specs").value || "{}"); }
  catch { return notify("Invalid product specs JSON", "warning"); }

  const body = {
    producer_id: pid,
    name: document.getElementById("prod_name").value,
    price: Number(document.getElementById("prod_price").value),
    quantity: Number(document.getElementById("prod_qty").value),
    specs,
    domain: document.getElementById("prod_domain").value,
  };
  const data = await fetchJSON("/products/add", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
  });
  setOut("producer_out", data);
  humanProducerView(body);
  notify("Product registered", "success");
}

// ==========================
// Negotiation (consumer)
// ==========================
async function startNegotiation() {
  let specs = {}, product;
  try { specs = JSON.parse(document.getElementById("specs").value || "{}"); }
  catch { return notify("Invalid specs JSON", "warning"); }
  try { product = JSON.parse(document.getElementById("product_json").value || "{}"); }
  catch { return notify("Invalid product JSON", "warning"); }

  const body = {
    product,
    consumer_request: {
      product_name: document.getElementById("product_name").value,
      quantity: Number(document.getElementById("quantity").value),
      budget: Number(document.getElementById("budget").value),
      specs,
    },
    num_producers: Number(document.getElementById("num_producers").value),
    num_rounds: Number(document.getElementById("num_rounds").value),
    use_llm: document.getElementById("use_llm").value === "true",
  };

  const data = await fetchJSON("/negotiation/start", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
  });
  setOut("start_out", data);
  humanStartView(data);
  if (data.session_id) {
    saveSession(data.session_id);
    setCurrentRound(1);
    notify("Negotiation started", "success");
    await fetchRound(getCurrentRound()); // auto fetch round 1
  }
}

// fetch a specific round (core)
async function fetchRound(roundNum) {
  const sessionId = getSession();
  const res = await fetch(`/negotiation/${sessionId}/round/${roundNum}`);
  if (res.status === 404) {
    notify("No offers for this round", "warning");
    return null;
  }
  const json = await res.json();
  setOut("round_out", json);
  renderOffersTable(json);
  return json;
}

// “Fetch” button in UI uses the input value (fix)
async function getRound() {
  const roundNum = Number(document.getElementById("round_number").value);
  if (roundNum < 1) { notify("Round must be >= 1", "warning"); return; }
  setCurrentRound(roundNum);
  const data = await fetchRound(roundNum);
  if (data) notify(`Round ${roundNum} loaded`, "info");
}

// prev / next buttons
async function prevRound() {
  const n = Math.max(1, getCurrentRound() - 1);
  setCurrentRound(n);
  const data = await fetchRound(n);
  if (data) notify(`Round ${n} loaded`, "info");
}
async function nextRound() {
  const n = getCurrentRound() + 1;
  setCurrentRound(n);
  const res = await fetch(`/negotiation/${getSession()}/round/${n}`);
  if (res.status === 404) {
    notify("No more rounds available", "warning");
    setCurrentRound(n - 1);
    return;
  }
  const json = await res.json();
  setOut("round_out", json);
  renderOffersTable(json);
  notify(`Round ${n} loaded`, "info");
}

// choose via manual form (optional)
async function chooseOffer() {
  const sessionId = getSession();
  const round = Number(document.getElementById("choose_round_number").value);
  const idx = Number(document.getElementById("choose_offer_index").value);
  const data = await fetchJSON(`/negotiation/${sessionId}/choose`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ round_number: round, offer_index: idx })
  });
  setOut("choose_out", data);
  humanChooseView(data);
  notify("Offer chosen (manual)", "success");
}

// finalize & summary
async function finalize() {
  const sessionId = getSession();
  const idx = Number(document.getElementById("chosen_deal_index").value);
  const data = await fetchJSON(`/negotiation/${sessionId}/finalize`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ chosen_deal_index: idx })
  });
  setOut("final_out", data);
  humanFinalView(data);
  notify("Negotiation finalized", "success");
  setTab("tab-summary");
}
async function summary() {
  const sessionId = getSession();
  const data = await fetchJSON(`/negotiation/${sessionId}/summary`);
  setOut("summary_out", data);
  humanSummaryView(data);
  notify("Summary loaded", "info");
}

// ===========================
// Wiring + bootstrap
// ===========================
function prefillIds() {
  const uid = localStorage.getItem("user_id");
  const cid = localStorage.getItem("consumer_id") || uid;
  const pid = localStorage.getItem("producer_id") || uid;
  const sid = localStorage.getItem("session_id");
  const C = id => document.getElementById(id);
  if (cid && C("consumer_id")) C("consumer_id").value = cid;
  if (pid && C("producer_id")) C("producer_id").value = pid;
  if (sid && C("session_id")) C("session_id").value = sid;
  if (sid && C("choose_session_id")) C("choose_session_id").value = sid;
  updateFootSession();
}

function wire() {
  const map = {
    btnSignup: signup,
    btnLogin: login,
    btnSubmitRequest: submitRequest,
    btnAddProduct: addProduct,
    btnStart: startNegotiation,
    btnRound: getRound,
    btnPrevRound: prevRound,
    btnNextRound: nextRound,
    btnChoose: chooseOffer,
    btnFinalize: finalize,
    btnSummary: summary,
  };
  for (const [id, fn] of Object.entries(map)) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
}

// init
initRole();
initTabs();
prefillIds();
wire();
