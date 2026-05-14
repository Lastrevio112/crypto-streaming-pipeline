// // ── Config ────────────────────────────────────────────
// const COINS = [
//   "AAVEUSDT","ADAUSDT","ARBUSDT","ASTERUSDT","AVAXUSDT","BABYUSDT","BANANAS31USDT","BIOUSDT","BNBUSDT","BTCUSDT",
//   "CHIPUSDT","DASHUSDT","DOGEUSDT","ENAUSDT","ETHUSDT","EURUSDT","FDUSDUSDT","FETUSDT","GIGGLEUSDT","LINKUSDT","LTCUSDT",
//   "LUNCUSDT","MEGAUSDT","ONDOUSDT","OPENUSDT","ORCAUSDT","ORDIUSDT","PARTIUSDT","PAXGUSDT","PENGUUSDT","PEPEUSDT",
//   "RLUSDUSDT","SOLUSDT","SUIUSDT","TAOUSDT","TONUSDT","TRXUSDT","TSTUSDT","UNIUSDT","WLFIUSDT","XAUTUSDT","XRPUSDT",
//   "XVGUSDT","ZECUSDT","ZENUSDT","ZKUSDT"
// ];

// const WS_URL = "/ws/trades";        // FastAPI WebSocket endpoint
// const MAX_LOG_ENTRIES = 200;        // cap DOM nodes in the log

// // ── State ─────────────────────────────────────────────
// let selectedCoin = "BTC";
// let logEntries   = [];              // ring buffer of raw message objects
// let ws           = null;

// // ── Coin selector ─────────────────────────────────────
// function initCoinSelector() {
//   const sel = document.getElementById("coin-select");
//   if (!sel) return;

//   COINS.forEach(c => {
//     const opt = document.createElement("option");
//     opt.value = c;
//     opt.textContent = c + "/USDT";
//     if (c === selectedCoin) opt.selected = true;
//     sel.appendChild(opt);
//   });

//   sel.addEventListener("change", () => {
//     selectedCoin = sel.value;
//     updateGrafanaIframes();
//     filterLog();
//   });
// }

// // ── Grafana iframes ───────────────────────────────────
// function updateGrafanaIframes() {
//   document.querySelectorAll(".grafana-frame").forEach(iframe => {
//     const url = new URL(iframe.src, window.location.origin);
//     url.searchParams.set("var-coin_symbol", selectedCoin);
//     iframe.src = url.toString();
//   });
// }

// // ── Log panel toggle ──────────────────────────────────
// function initLogPanel() {
//   const panel     = document.getElementById("log-panel");
//   const toggleBtn = document.getElementById("log-toggle");
//   const openBtn   = document.getElementById("log-open-btn");
//   if (!panel) return;

//   toggleBtn?.addEventListener("click", () => {
//     panel.classList.add("collapsed");
//     openBtn?.classList.add("visible");
//   });

//   openBtn?.addEventListener("click", () => {
//     panel.classList.remove("collapsed");
//     openBtn?.classList.remove("visible");
//   });
// }

// // ── Log rendering ─────────────────────────────────────
// function filterLog() {
//   document.querySelectorAll(".log-entry").forEach(el => {
//     el.classList.toggle("visible", el.dataset.coin === selectedCoin);
//   });
// }

// function appendLogEntry(msg) {
//   const container = document.getElementById("log-entries");
//   if (!container) return;

//   // Enforce cap
//   if (logEntries.length >= MAX_LOG_ENTRIES) {
//     const oldest = container.lastElementChild;
//     if (oldest) container.removeChild(oldest);
//     logEntries.shift();
//   }

//   logEntries.unshift(msg);

//   const entry = document.createElement("div");
//   entry.className = "log-entry" + (msg.symbol === selectedCoin ? " visible" : "");
//   entry.dataset.coin = msg.symbol;

//   const sideClass = msg.side === "buy" ? "log-side-buy" : "log-side-sell";
//   const time = new Date(msg.timestamp).toLocaleTimeString("en-GB", { hour12: false });

//   entry.innerHTML = `
//     <div class="log-entry-header">
//       <span class="log-symbol">${msg.symbol}/USDT</span>
//       <span class="log-time">${time}</span>
//     </div>
//     <div class="log-price">
//       $${Number(msg.price).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
//       <span class="${sideClass}">${msg.side.toUpperCase()}</span>
//     </div>
//     <div class="log-qty">${Number(msg.quantity).toFixed(6)} ${msg.symbol}</div>
//   `;

//   // Batch DOM write on next frame to avoid layout thrashing
//   requestAnimationFrame(() => container.prepend(entry));
// }

// // ── WebSocket ─────────────────────────────────────────
// // function connectWebSocket() {
// //   const proto = location.protocol === "https:" ? "wss" : "ws";
// //   ws = new WebSocket(`${proto}://${location.host}${WS_URL}`);

// //   ws.onmessage = event => {
// //     try {
// //       const msg = JSON.parse(event.data);
// //       appendLogEntry(msg);
// //     } catch (e) {
// //       console.warn("Bad WS message:", event.data);
// //     }
// //   };

// //   ws.onclose = () => {
// //     // Reconnect after 3 seconds
// //     setTimeout(connectWebSocket, 3000);
// //   };

// //   ws.onerror = err => {
// //     console.error("WebSocket error:", err);
// //     ws.close();
// //   };
// // }

// // ── Init ──────────────────────────────────────────────
// document.addEventListener("DOMContentLoaded", () => {
//   initCoinSelector();
//   initLogPanel();
//   connectWebSocket();
// });