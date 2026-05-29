/**
 * MediCase patient mini web app.
 *
 * Opened via QR code with ?case=<id>&lang=<code>. Conducts an in-language,
 * voice-first triage with a tap-card fallback for non-verbal / low-literacy
 * patients. Answers are POSTed to the case API (stubbed here).
 *
 * Privacy: nothing is persisted on the device; the session lives in memory
 * and is cleared when the page unloads.
 */
(function () {
  "use strict";

  // ---- session state (in-memory only) ------------------------------------
  const params = new URLSearchParams(location.search);
  const caseId = params.get("case") || "demo-local";
  let lang = (params.get("lang") || navigator.language || "en")
    .toLowerCase()
    .split("-")[0];

  const C = window.TRIAGE_CONTENT;
  if (!C[lang]) lang = "en";
  const t = C[lang];

  const app = document.getElementById("app");
  const privacy = document.getElementById("privacy");

  if (t.rtl) document.documentElement.setAttribute("dir", "rtl");
  document.documentElement.setAttribute("lang", lang);

  const answers = []; // {question, answer, mode}
  let qIndex = 0;

  const CASE_API =
    window.CASE_API_URL ||
    (location.hostname === "localhost" ? "http://localhost:8787" : "");

  // ---- speech (TTS + STT), gracefully optional ---------------------------
  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = t.bcp47;
      u.rate = 0.95;
      window.speechSynthesis.speak(u);
    } catch (e) {
      /* TTS not available — text is on screen anyway */
    }
  }

  function makeRecognizer() {
    const SR =
      window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SR) return null;
    const r = new SR();
    r.lang = t.bcp47;
    r.interimResults = false;
    r.maxAlternatives = 1;
    return r;
  }

  // ---- rendering ---------------------------------------------------------
  function header() {
    return `
      <div class="hdr">
        <div class="pulse"></div>
        <div>
          <h1>MediCase</h1>
          <div class="sub">Case ${escapeHtml(caseId)}</div>
        </div>
      </div>`;
  }

  function renderReassure(next) {
    app.innerHTML =
      header() +
      `<div class="reassure"><p>${escapeHtml(t.reassure)}</p></div>
       <button class="btn btn-primary" id="start">▶︎</button>`;
    speak(t.reassure);
    document.getElementById("start").onclick = next;
  }

  function renderQuestion() {
    if (qIndex >= t.questions.length) return renderDone();
    const qText = t.questions[qIndex];
    const isPain = qIndex === 1; // "how strong is the pain 0-10"
    const isBody = qIndex === 0; // "where does it hurt"

    let extra = "";
    if (isPain) extra = painScale();
    else if (isBody) extra = bodyMap();

    app.innerHTML =
      header() +
      `<div class="q-card">
         <div class="q-progress">${qIndex + 1} / ${t.questions.length}</div>
         <p class="q-text">${escapeHtml(qText)}</p>
         <div class="heard" id="heard"></div>
         <button class="btn btn-mic" id="mic">🎙️ ${escapeHtml(t.micHint)}</button>
         <button class="btn btn-speak" id="again">🔊 ${escapeHtml(t.speakAgain)}</button>
         ${extra}
       </div>`;

    speak(qText);

    document.getElementById("again").onclick = () => speak(qText);
    document.getElementById("mic").onclick = startListening;

    if (isPain) wirePainScale();
    if (isBody) wireBodyMap();
  }

  function painScale() {
    const colors = [
      "#1a7f4b", "#3c9a3c", "#7cb342", "#c0ca33", "#fdd835",
      "#ffb300", "#fb8c00", "#f4511e", "#e53935", "#c62828", "#8e0000",
    ];
    let cells = "";
    for (let i = 0; i <= 10; i++) {
      cells += `<button style="background:${colors[i]}" data-pain="${i}">${i}</button>`;
    }
    return `<p class="q-progress">${escapeHtml(t.painPrompt)}</p>
            <div class="scale">${cells}</div>`;
  }

  function wirePainScale() {
    app.querySelectorAll("[data-pain]").forEach((b) => {
      b.onclick = () => recordAnswer(`pain=${b.dataset.pain}`, "tap");
    });
  }

  function bodyMap() {
    const parts = Object.keys(t.body);
    let cells = "";
    for (const p of parts) {
      cells += `<button class="tap" data-body="${p}">
                  <span class="emoji">${window.BODY_EMOJI[p] || "•"}</span>
                  <span>${escapeHtml(t.body[p])}</span>
                </button>`;
    }
    return `<p class="q-progress">${escapeHtml(t.bodyPrompt)}</p>
            <div class="tapgrid">${cells}</div>`;
  }

  function wireBodyMap() {
    app.querySelectorAll("[data-body]").forEach((b) => {
      b.onclick = () => {
        app.querySelectorAll("[data-body]").forEach((x) =>
          x.classList.remove("selected")
        );
        b.classList.add("selected");
        recordAnswer(`location=${b.dataset.body}`, "tap");
      };
    });
  }

  function startListening() {
    const rec = makeRecognizer();
    const mic = document.getElementById("mic");
    const heard = document.getElementById("heard");
    if (!rec) {
      heard.textContent = "🎙️ —"; // STT unavailable; tap-cards still work
      return;
    }
    mic.classList.add("listening");
    rec.onresult = (ev) => {
      const text = ev.results[0][0].transcript;
      heard.textContent = text;
      recordAnswer(text, "voice");
    };
    rec.onerror = () => {
      mic.classList.remove("listening");
    };
    rec.onend = () => mic.classList.remove("listening");
    try {
      rec.start();
    } catch (e) {
      mic.classList.remove("listening");
    }
  }

  function recordAnswer(answer, mode) {
    answers.push({ question: t.questions[qIndex], answer, mode });
    qIndex += 1;
    setTimeout(renderQuestion, 450);
  }

  function renderDone() {
    submitAnswers();
    app.innerHTML =
      header() +
      `<div class="done">
         <div class="check">✓</div>
         <h2>${escapeHtml(t.done)}</h2>
       </div>`;
    speak(t.done);
  }

  function submitAnswers() {
    const payload = {
      case_id: caseId,
      language: lang,
      answers,
      submitted_at: new Date().toISOString(),
    };
    // Best-effort POST; demo works even with no backend.
    if (CASE_API) {
      try {
        fetch(`${CASE_API}/api/case/${encodeURIComponent(caseId)}/intake`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          keepalive: true,
        }).catch(() => {});
      } catch (e) {
        /* offline demo — ignore */
      }
    }
    // Surface for debugging / demo screen-recording.
    console.log("[MediCase intake payload]", payload);
    window.__lastIntake = payload;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  // ---- privacy + lifecycle ----------------------------------------------
  privacy.textContent =
    "MediCase • Your answers are sent only to the on-site medical team. " +
    "Nothing is stored on this phone.";
  window.addEventListener("pagehide", () => {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  });

  // ---- go ----------------------------------------------------------------
  renderReassure(renderQuestion);
})();
