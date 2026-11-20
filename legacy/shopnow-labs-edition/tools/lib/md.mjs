// Minimal, dependency-free markdown -> HTML for the guide bodies.
// Supports: h2/h3, paragraphs, ul/ol, blockquote, bold, italic, inline code,
// links, horizontal rules, and a callout block:
//   :::note Label text
//   body
//   :::

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function inline(text, base = "") {
  let t = esc(text);
  t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, label, href) => {
    if (/^https?:\/\//.test(href)) {
      // External link. If it is a purchasable product page it must be tagged,
      // so the guide body never emits a bare amazon.com/dp/ link.
      return `<a href="${href}" target="_blank" rel="nofollow noopener">${label}</a>`;
    }
    // Root-relative internal link -> prefix the Pages base path.
    const to = href.startsWith("/") ? base + href : href;
    return `<a href="${to}">${label}</a>`;
  });
  return t;
}

export function md(src, opts = {}) {
  const base = opts.base || "";
  const lines = String(src).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let i = 0;
  let listType = null;

  const closeList = () => {
    if (listType) { out.push(`</${listType}>`); listType = null; }
  };

  while (i < lines.length) {
    const line = lines[i];

    // callout
    if (/^:::/.test(line)) {
      closeList();
      const kind = line.replace(/^:::+/, "").trim();
      const body = [];
      i++;
      while (i < lines.length && !/^:::\s*$/.test(lines[i])) { body.push(lines[i]); i++; }
      i++;
      const cls = /warn/i.test(kind) ? " callout--warn" : /verify/i.test(kind) ? " callout--verify" : "";
      const label = kind.replace(/^(note|warn|verify)\s*·?\s*/i, "").trim();
      out.push(`<div class="callout${cls}">${label ? `<span class="callout__label">${esc(label)}</span>` : ""}${md(body.join("\n"), { base })}</div>`);
      continue;
    }

    if (/^\s*$/.test(line)) { closeList(); i++; continue; }
    if (/^---+$/.test(line)) { closeList(); out.push("<hr>"); i++; continue; }

    const h = line.match(/^(#{2,4})\s+(.*)$/);
    if (h) {
      closeList();
      const lvl = h[1].length;
      out.push(`<h${lvl}>${inline(h[2], base)}</h${lvl}>`);
      i++; continue;
    }

    const ul = line.match(/^\s*[-*]\s+(.*)$/);
    if (ul) {
      if (listType !== "ul") { closeList(); out.push("<ul>"); listType = "ul"; }
      out.push(`<li>${inline(ul[1], base)}</li>`);
      i++; continue;
    }

    const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ol) {
      if (listType !== "ol") { closeList(); out.push("<ol>"); listType = "ol"; }
      out.push(`<li>${inline(ol[1], base)}</li>`);
      i++; continue;
    }

    const bq = line.match(/^>\s?(.*)$/);
    if (bq) {
      closeList();
      const body = [bq[1]];
      i++;
      while (i < lines.length && /^>\s?/.test(lines[i])) { body.push(lines[i].replace(/^>\s?/, "")); i++; }
      out.push(`<blockquote><p>${inline(body.join(" "), base)}</p></blockquote>`);
      continue;
    }

    // paragraph: gather until blank / block start
    closeList();
    const para = [line];
    i++;
    while (i < lines.length && lines[i].trim() !== "" && !/^(#{2,4}\s|[-*]\s|\d+[.)]\s|>|:::|---+$)/.test(lines[i])) {
      para.push(lines[i]); i++;
    }
    out.push(`<p>${inline(para.join(" "), base)}</p>`);
  }
  closeList();
  return out.join("\n");
}

export { esc };
