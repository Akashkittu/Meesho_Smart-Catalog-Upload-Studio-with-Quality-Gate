
async function fetchSchema(category) {
  const res = await fetch(`/schema?category=${encodeURIComponent(category || "")}`);
  return res.json();
}

const categoryEl = document.getElementById("category");
const attrsEl = document.getElementById("attrs");
const dropEl = document.getElementById("drop");
const imagesEl = document.getElementById("images");
const previewEl = document.getElementById("preview");
const runBtn = document.getElementById("run");
const scoreEl = document.getElementById("score");
const ringEl = document.getElementById("ring");
const gateEl = document.getElementById("gate");
const minqEl = document.getElementById("minq");
const knownEl = document.getElementById("known");
const issuesEl = document.getElementById("issues");
const toastEl = document.getElementById("toast");

const MINQ = Number.isFinite(+window.MIN_QUALITY) ? +window.MIN_QUALITY : 70;
minqEl.textContent = MINQ;
window.MIN_QUALITY = MINQ; // keep a reliable global


let files = [];

function toast(msg){
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  setTimeout(()=> toastEl.classList.remove("show"), 2000);
}

async function init() {
  const cats = ["T-Shirt", "Saree", "Footwear"];
  for (const c of cats) {
    const opt = document.createElement("option");
    opt.value = c; opt.textContent = c;
    categoryEl.appendChild(opt);
  }
  await loadSchema();
}
async function loadSchema() {
  const cat = categoryEl.value || "T-Shirt";
  const data = await fetchSchema(cat);
  attrsEl.innerHTML = "";
  (data.required || []).forEach(k => {
    const wrap = document.createElement("div");
    wrap.className = "kv-item";
    wrap.innerHTML = `<div class="key">${k}</div><div class="val"><input data-key="${k}" placeholder="${k}"/></div>`;
    attrsEl.appendChild(wrap);
  });
  updateAttrProgress();
  attrsEl.querySelectorAll("input").forEach(i => i.addEventListener("input", updateAttrProgress));
}

function updateAttrProgress(){
  const inputs = attrsEl.querySelectorAll("input[data-key]");
  const total = inputs.length || 1;
  let filled = 0;
  inputs.forEach(i => { if((i.value||"").trim().length>0) filled++; });
  const pct = Math.round(100*filled/total);
  document.getElementById("attrBar").style.width = pct+"%";
  document.getElementById("attrPct").textContent = pct + "% complete";
}

categoryEl.addEventListener("change", loadSchema);

dropEl.addEventListener("click", () => imagesEl.click());
["dragover","dragenter"].forEach(ev=> dropEl.addEventListener(ev, e => { e.preventDefault(); dropEl.classList.add("drag"); }));
["dragleave","drop"].forEach(ev=> dropEl.addEventListener(ev, e => { e.preventDefault(); dropEl.classList.remove("drag"); }));
dropEl.addEventListener("drop", e => { files = Array.from(e.dataTransfer.files || []); renderPreview(); });
imagesEl.addEventListener("change", e => { files = Array.from(e.target.files || []); renderPreview(); });

function renderPreview() {
  previewEl.innerHTML = "";
  files.forEach(f => {
    const div = document.createElement("div");
    div.className = "pill";
    div.textContent = f.name;
    previewEl.appendChild(div);
  });
}

function animateScore(val){
  scoreEl.textContent = val;
  ringEl.style.setProperty("--val", val);
  const threshold = window.MIN_QUALITY ?? 70;
  ringEl.classList.toggle("pass", val >= threshold);
  ringEl.classList.toggle("fail", val < threshold);
}


runBtn.addEventListener("click", async () => {
  const inputs = attrsEl.querySelectorAll("input[data-key]");
  const attrs = {};
  inputs.forEach(inp => attrs[inp.dataset.key] = inp.value.trim());
  const known = (knownEl.value || "").split(",").map(s => s.trim()).filter(Boolean);
  const fd = new FormData();
  files.forEach(f => fd.append("images", f));
  const payload = { category: categoryEl.value || "T-Shirt", attrs, known_hashes: known };
  fd.append("payload", JSON.stringify(payload));
  gateEl.textContent = "Checking…";

  const res = await fetch("/score", { method: "POST", body: fd });
  if (!res.ok) {
    const text = await res.text();
    issuesEl.innerHTML = `<div class="issue"><b>Server error ${res.status}</b><div class="tip">${text}</div></div>`;
    gateEl.textContent = "Error — see details below.";
    toast("Server error");
    return;
  }
  const data = await res.json();


  animateScore(data.quality_score);
  gateEl.textContent = data.gate_pass ? `Pass (≥ ${data.gate_threshold})` : `Fail (≥ ${data.gate_threshold})`;

  issuesEl.innerHTML = "";
  if((data.issues||[]).length === 0){
    issuesEl.innerHTML = `<div class="small">No issues—good to go!</div>`;
  } else {
    (data.issues || []).forEach(i => {
      const d = document.createElement("div");
      d.className = "issue";
      d.innerHTML = `<b>${i.message}</b><div class="tip">${i.tip}</div>`;
      issuesEl.appendChild(d);
    });
  }
  toast("Scoring complete");
});

init();
