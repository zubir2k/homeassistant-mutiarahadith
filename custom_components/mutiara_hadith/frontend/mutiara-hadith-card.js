/*
 * Mutiara Hadith card for Home Assistant.
 * Shipped and auto-loaded by the mutiara_hadith integration.
 * Content © JAKIM (MyHadith). Amiri font: SIL Open Font License 1.1.
 */
const CARD_VERSION = "0.4.1";
const BASE = new URL(".", import.meta.url).pathname;

const STAR = (() => {
  const s = (a) => {
    const p = [];
    for (let k = 0; k < 8; k++) {
      let t = (k * Math.PI) / 4;
      p.push([a * Math.SQRT2 * Math.cos(t), a * Math.SQRT2 * Math.sin(t)]);
      t += Math.PI / 8;
      const r = a / Math.cos(Math.PI / 8);
      p.push([r * Math.cos(t), r * Math.sin(t)]);
    }
    return "M" + p.map((q) => q.map((v) => v.toFixed(2)).join(" ")).join("L") + "Z";
  };
  const a1 = 32.5, a2 = a1 * 0.79, a3 = a2 * 0.8;
  return s(a1) + s(a2) + s(a3);
})();

// @font-face must live in the document, not the shadow root.
if (!document.getElementById("mutiara-hadith-font")) {
  const st = document.createElement("style");
  st.id = "mutiara-hadith-font";
  st.textContent = `@font-face{font-family:"MH Amiri";src:url("${BASE}Amiri-Regular.ttf") format("truetype");font-display:swap;}`;
  document.head.appendChild(st);
}

const TABS = [
  ["maksud", "Maksud"],
  ["penghayatan", "Penghayatan"],
  ["butiran", "Butiran"],
];
const ARABIC = /[\u0600-\u06FF]/;

const esc = (v) =>
  String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const paras = (text) =>
  String(text ?? "")
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => `<p>${esc(p).replace(/\n/g, " ")}</p>`)
    .join("");

/** Split the matan from its trailing "]التخريج : ...[" note. */
function splitMatan(matan) {
  const text = String(matan ?? "").trim();
  const i = text.search(/[\[\]]?\s*التخريج/);
  if (i <= 0) return { matan: text, takhrij: "" };
  return {
    matan: text.slice(0, i).trim(),
    takhrij: text.slice(i).replace(/^[\[\]\s]+|[\[\]\s]+$/g, "").trim(),
  };
}

/** "Latin - Arabic" or "Arabic - Latin" → html with the Arabic part set in Amiri. */
function mixed(value) {
  return String(value ?? "")
    .split(/\s+-\s+/)
    .map((part) => (ARABIC.test(part) ? `<span class="ar-inl" dir="rtl">${esc(part)}</span>` : esc(part)))
    .join(" · ");
}

class MutiaraHadithCard extends HTMLElement {
  static getStubConfig() {
    return { entity: "sensor.mutiara_hadith" };
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { filter: { integration: "mutiara_hadith" } } } },
        {
          name: "default_tab",
          selector: { select: { mode: "dropdown", options: TABS.map(([value, label]) => ({ value, label })) } },
        },
        { name: "pane_height", selector: { number: { min: 0, max: 800, step: 10, mode: "box", unit_of_measurement: "px" } } },
        { name: "show_takhrij", selector: { boolean: {} } },
        { name: "show_attribution", selector: { boolean: {} } },
      ],
      computeLabel: (s) =>
        ({
          entity: "Entity",
          default_tab: "Default tab",
          pane_height: "Tab height (0 = grow to fit)",
          show_takhrij: "Show takhrij under the matan",
          show_attribution: "Show source line",
        })[s.name],
    };
  }

  setConfig(config) {
    if (!config) throw new Error("Invalid configuration");
    this._config = {
      entity: "sensor.mutiara_hadith",
      default_tab: "maksud",
      pane_height: 220,
      show_takhrij: true,
      show_attribution: true,
      ...config,
    };
    this._tab = this._config.default_tab;
    this._hadithId = undefined;
    this._render();
  }

  set hass(hass) {
    const old = this._hass;
    this._hass = hass;
    const st = hass.states[this._config?.entity];
    const prev = old?.states[this._config?.entity];
    if (!old || st !== prev || old.themes?.darkMode !== hass.themes?.darkMode) this._render();
  }

  getCardSize() {
    return 9;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, rows: "auto" };
  }

  _render() {
    if (!this._config || !this._hass) return;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    const st = this._hass.states[this._config.entity];
    const dark = !!this._hass.themes?.darkMode;

    if (!st) {
      this.shadowRoot.innerHTML = `${this._style(dark)}<ha-card><div class="empty">Entity not found: ${esc(this._config.entity)}</div></ha-card>`;
      return;
    }
    if (st.state === "unavailable" || st.state === "unknown") {
      this.shadowRoot.innerHTML = `${this._style(dark)}<ha-card>${this._header("")}<div class="empty">Mutiara Hadith tidak tersedia buat masa ini.</div></ha-card>`;
      return;
    }

    const a = st.attributes;
    if (a.hadith_id !== this._hadithId) {
      // New hadith: go back to the default tab.
      this._hadithId = a.hadith_id;
      this._tab = this._config.default_tab;
    }
    const { matan, takhrij } = splitMatan(a.matan);
    const chip = [a.koleksi, a.nombor_hadith ? `No. ${a.nombor_hadith}` : ""].filter(Boolean).join(" · ");
    const rujukan = Array.isArray(a.sumber_rujukan) ? a.sumber_rujukan : [];
    const h = Number(this._config.pane_height) || 0;

    const meta = [
      ["Kitab", a.kitab],
      ["Bab", a.bab],
      ["Perawi", a.perawi],
    ]
      .filter(([, v]) => v)
      .map(([k, v]) => `<dt>${k}</dt><dd>${mixed(v)}</dd>`)
      .join("");
    const status = a.status ? `<dt>Darjat</dt><dd><span class="st">${esc(a.status)}</span></dd>` : "";
    const ruj = rujukan.length
      ? `<div class="ruj"><div class="ruj-h">Sumber rujukan</div><ol>${rujukan.map((r) => `<li>${esc(r)}</li>`).join("")}</ol></div>`
      : "";

    const panes = {
      maksud: `<blockquote>${paras(a.maksud) || "<p>-</p>"}</blockquote>`,
      penghayatan: paras(a.penghayatan) || `<p class="muted">Tiada penghayatan untuk hadith ini.</p>`,
      butiran: `<dl>${meta}${status}</dl>${ruj}`,
    };

    this.shadowRoot.innerHTML = `
      ${this._style(dark)}
      <ha-card>
        ${this._header(chip)}
        <h2 class="title">${esc(st.state)}</h2>
        ${matan ? `<div class="matan">
          <svg class="wm" viewBox="-50 -50 100 100" aria-hidden="true"><path d="${STAR}" fill-rule="evenodd"/></svg>
          <div class="ar" dir="rtl" lang="ar">${esc(matan).replace(/\n+/g, " ")}</div>
          ${this._config.show_takhrij && takhrij ? `<div class="takhrij" dir="rtl" lang="ar">${esc(takhrij)}</div>` : ""}
        </div>` : ""}
        <div class="tabs" role="tablist">
          ${TABS.map(([k, label]) => `<button role="tab" class="tab ${k === this._tab ? "on" : ""}" data-tab="${k}" aria-selected="${k === this._tab}">${label}</button>`).join("")}
        </div>
        <div class="pane ${h ? "fixed" : ""}" style="${h ? `height:${h}px` : ""}" role="tabpanel">${panes[this._tab] ?? panes.maksud}</div>
        <div class="ft">
          ${this._config.show_attribution ? `<span class="attr">${esc(a.attribution ?? "Sumber: MyHadith, JAKIM")}</span>` : "<span></span>"}
          ${a.url ? `<a class="btn" href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">Baca di MyHadith ↗</a>` : ""}
        </div>
      </ha-card>`;

    this.shadowRoot.querySelectorAll(".tab").forEach((b) =>
      b.addEventListener("click", () => {
        this._tab = b.dataset.tab;
        this._render();
      })
    );
  }

  _header(chip) {
    return `<div class="hd">
      <svg class="logo" viewBox="-50 -50 100 100" aria-hidden="true"><path d="${STAR}" fill-rule="evenodd"/></svg>
      <span class="brand">Mutiara Hadith</span>
      ${chip ? `<span class="chip">${esc(chip)}</span>` : ""}
    </div>`;
  }

  _style(dark) {
    const g = this._config.accent || (dark ? "#5fc49b" : "#2a7f5f");
    return `<style>
      :host{--mh-g:${g};--mh-soft:color-mix(in srgb,var(--mh-g) ${dark ? 12 : 9}%,var(--card-background-color,#fff));}
      ha-card{overflow:hidden;color:var(--primary-text-color);}
      .hd{display:flex;align-items:center;gap:10px;padding:16px 16px 4px;}
      .logo{width:24px;height:24px;flex:none;fill:var(--mh-g);}
      .brand{font-weight:600;font-size:15px;color:var(--mh-g);}
      .chip{margin-left:auto;font-size:11.5px;font-weight:500;color:var(--mh-g);background:var(--mh-soft);padding:4px 10px;border-radius:999px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60%;}
      .title{font-size:20px;font-weight:700;line-height:1.3;margin:6px 16px 12px;}
      .matan{position:relative;margin:0 12px;padding:16px 16px 12px;background:var(--mh-soft);border-radius:10px;overflow:hidden;}
      .wm{position:absolute;left:-30px;top:-30px;width:150px;height:150px;fill:color-mix(in srgb,var(--mh-g) 8%,transparent);}
      .ar{position:relative;text-align:right;font-family:"MH Amiri","Amiri","Noto Naskh Arabic",serif;font-size:22px;line-height:2;}
      .takhrij{position:relative;text-align:right;font-family:"MH Amiri","Amiri",serif;font-size:13.5px;line-height:1.8;color:var(--secondary-text-color);margin-top:8px;padding-top:8px;border-top:1px dashed color-mix(in srgb,var(--mh-g) 30%,transparent);}
      .tabs{display:flex;gap:4px;margin:12px 12px 0;padding:4px;background:var(--secondary-background-color,rgba(127,127,127,.1));border-radius:10px;}
      .tab{flex:1;border:0;background:none;cursor:pointer;font:inherit;font-size:13px;font-weight:600;color:var(--secondary-text-color);padding:7px 0;border-radius:7px;}
      .tab.on{background:var(--card-background-color,#fff);color:var(--mh-g);box-shadow:0 1px 2px rgba(0,0,0,.15);}
      .tab:focus-visible{outline:2px solid var(--mh-g);}
      .pane{padding:12px 16px 4px;font-size:14px;line-height:1.65;}
      .pane.fixed{overflow-y:auto;scrollbar-width:thin;}
      .pane p{margin:0 0 10px;}
      blockquote{margin:0;padding-left:12px;border-left:3px solid var(--mh-g);}
      dl{display:grid;grid-template-columns:72px 1fr;gap:8px 10px;margin:0;font-size:13px;}
      dt{color:var(--secondary-text-color);} dd{margin:0;}
      .ar-inl{font-family:"MH Amiri","Amiri",serif;font-size:15px;}
      .st{display:inline-block;font-size:11px;padding:2px 8px;border-radius:6px;background:var(--secondary-background-color,rgba(127,127,127,.15));color:var(--secondary-text-color);}
      .ruj{margin-top:12px;font-size:13px;} .ruj-h{color:var(--secondary-text-color);margin-bottom:4px;} .ruj ol{margin:0;padding-left:18px;}
      .muted{color:var(--secondary-text-color);}
      .ft{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px 16px;margin-top:8px;border-top:1px solid var(--divider-color);}
      .attr{font-size:10.5px;line-height:1.4;color:var(--secondary-text-color);}
      .btn{font-size:12.5px;font-weight:600;color:${dark ? "#0f1a15" : "#fff"};background:var(--mh-g);padding:8px 14px;border-radius:8px;white-space:nowrap;text-decoration:none;}
      .empty{padding:16px;color:var(--secondary-text-color);}
    </style>`;
  }
}

if (!customElements.get("mutiara-hadith-card")) {
  customElements.define("mutiara-hadith-card", MutiaraHadithCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "mutiara-hadith-card",
    name: "Mutiara Hadith",
    description: "Mutiara Hadith pilihan JAKIM (MyHadith): matan, maksud, penghayatan dan butiran.",
    preview: true,
    documentationURL: "https://github.com/zubir2k/homeassistant-mutiarahadith",
  });
  console.info(`%c MUTIARA-HADITH-CARD %c ${CARD_VERSION} `, "color:#fff;background:#2a7f5f;font-weight:700", "color:#2a7f5f");
}
