/* Malto Maia - admin: toggles AJAX, edicao NA CELULA (estilo planilha), buscar/filtrar/ordenar. */
(function () {
  "use strict";

  function csrfFrom(el) {
    var i = el.querySelector('input[name="csrfmiddlewaretoken"]');
    return i ? i.value : "";
  }
  function ajaxHeaders(token) {
    var h = { "X-Requested-With": "XMLHttpRequest" };
    if (token) h["X-CSRFToken"] = token;
    return h;
  }

  /* ----- Toggle sem reload (delegado) ----- */
  document.addEventListener("submit", function (e) {
    var form = e.target.closest ? e.target.closest("form.js-toggle") : null;
    if (!form) return;
    e.preventDefault();
    var sw = form.querySelector(".switch");
    if (sw) sw.disabled = true;
    fetch(form.action, { method: "POST", headers: ajaxHeaders(csrfFrom(form)), body: new FormData(form) })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
      .then(function (data) {
        if (sw && typeof data.on === "boolean") sw.classList.toggle("on", data.on);
        if (data.stats) {
          Object.keys(data.stats).forEach(function (k) {
            var el = document.querySelector('[data-stat="' + k + '"]');
            if (el) el.textContent = data.stats[k];
          });
        }
      })
      .catch(function () { form.submit(); })
      .then(function () { if (sw) sw.disabled = false; });
  });

  /* ----- Editar NA CELULA (in-place; a linha vira editavel ali mesmo) ----- */
  var editingRow = null, editingHTML = "";

  function closeEditor(restore) {
    if (!editingRow) return;
    if (restore) editingRow.outerHTML = editingHTML;
    editingRow = null; editingHTML = "";
  }

  function openEditor(link) {
    var tr = link.closest("tr");
    if (!tr) return;
    if (editingRow && editingRow !== tr) closeEditor(true);
    editingRow = tr;
    editingHTML = tr.outerHTML;
    fetch(link.getAttribute("href"), { headers: ajaxHeaders() })
      .then(function (r) { return r.text(); })
      .then(function (cells) {
        tr.classList.add("editing");
        tr.innerHTML = cells;            // resposta = as proprias <td> editaveis
        var f = tr.querySelector("input, select, textarea");
        if (f) { f.focus(); if (f.select) f.select(); }
      });
  }

  function saveEditor(btn) {
    if (!editingRow) return;
    var row = editingRow;
    var body = new FormData();
    [].forEach.call(row.querySelectorAll("[name]"), function (el) {
      if (el.name === "csrfmiddlewaretoken") return;
      body.append(el.name, el.value);
    });
    // switches/estrela: presentes so quando ligados (semantica de checkbox)
    [].forEach.call(row.querySelectorAll(".js-ed-toggle.on"), function (b) {
      var f = b.getAttribute("data-field");
      if (f) body.append(f, "on");
    });
    btn.disabled = true;
    fetch(btn.getAttribute("data-action"), { method: "POST", headers: ajaxHeaders(csrfFrom(row)), body: body })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok && data.row) {
          row.outerHTML = data.row;       // volta a linha normal, ja atualizada
          editingRow = null; editingHTML = "";
          if (data.stats) {
            Object.keys(data.stats).forEach(function (k) {
              var el = document.querySelector('[data-stat="' + k + '"]');
              if (el) el.textContent = data.stats[k];
            });
          }
        } else if (data.rowedit) {
          row.innerHTML = data.rowedit;   // erros de validacao: remostra com aviso
          var f = row.querySelector("input, select, textarea");
          if (f) f.focus();
        }
      })
      .catch(function () { if (btn) btn.disabled = false; });
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    var editLink = e.target.closest(".js-edit");
    if (editLink) { e.preventDefault(); openEditor(editLink); return; }
    var toggle = e.target.closest(".js-ed-toggle");
    if (toggle) { e.preventDefault(); toggle.classList.toggle("on"); return; }
    var saveBtn = e.target.closest(".js-ed-save");
    if (saveBtn) { e.preventDefault(); saveEditor(saveBtn); return; }
    if (e.target.closest(".js-ed-cancel") || e.target.closest("[data-close]")) {
      if (editingRow) { e.preventDefault(); closeEditor(true); }
    }
  });

  // Teclado: Enter salva (fora de textarea), Esc cancela
  document.addEventListener("keydown", function (e) {
    if (!editingRow) return;
    if (e.key === "Escape") { e.preventDefault(); closeEditor(true); return; }
    if (e.key === "Enter" && editingRow.contains(e.target) && e.target.tagName !== "TEXTAREA") {
      var btn = editingRow.querySelector(".js-ed-save");
      if (btn) { e.preventDefault(); saveEditor(btn); }
    }
  });

  /* ----- Tabela tipo Excel: buscar + filtrar categoria + ordenar ----- */
  var table = document.querySelector(".adm-table");
  var search = document.querySelector('.adm-toolbar input[type="search"]');
  var catFilter = document.getElementById("filter-cat");
  function cellText(tr, idx) { var td = tr.children[idx]; return td ? td.textContent.trim() : ""; }
  function rows() { return table ? [].slice.call(table.querySelectorAll("tbody tr")) : []; }

  var catIdx = -1;
  if (table) {
    [].forEach.call(table.querySelectorAll("thead th"), function (th, i) {
      if (th.getAttribute("data-col") === "cat") catIdx = i;
    });
  }

  // popula o filtro de categoria com os valores presentes na tabela
  if (table && catFilter && catIdx >= 0) {
    var cats = {};
    rows().forEach(function (tr) { var v = cellText(tr, catIdx); if (v) cats[v] = 1; });
    Object.keys(cats).sort(function (a, b) { return a.localeCompare(b, "pt"); }).forEach(function (c) {
      var o = document.createElement("option");
      o.value = c.toLowerCase(); o.textContent = c;
      catFilter.appendChild(o);
    });
  }

  function applyFilters() {
    var q = search ? search.value.trim().toLowerCase() : "";
    var cat = catFilter ? catFilter.value : "";
    rows().forEach(function (tr) {
      if (tr.classList.contains("editing")) return;
      var okText = !q || tr.textContent.toLowerCase().indexOf(q) >= 0;
      var okCat = !cat || (catIdx >= 0 && cellText(tr, catIdx).toLowerCase() === cat);
      tr.style.display = okText && okCat ? "" : "none";
    });
  }
  if (search) {
    var sf = search.closest("form");
    if (sf) sf.addEventListener("submit", function (e) { e.preventDefault(); });
    search.addEventListener("input", applyFilters);
  }
  if (catFilter) catFilter.addEventListener("change", applyFilters);

  if (table) {
    [].forEach.call(table.querySelectorAll("thead th[data-sort]"), function (th) {
      var idx = [].indexOf.call(th.parentNode.children, th);
      var numeric = th.getAttribute("data-sort") === "num";
      th.addEventListener("click", function () {
        var asc = th.getAttribute("data-dir") !== "asc";
        [].forEach.call(th.parentNode.children, function (t) { t.removeAttribute("data-dir"); });
        th.setAttribute("data-dir", asc ? "asc" : "desc");
        var tbody = table.querySelector("tbody");
        var trs = [].slice.call(tbody.querySelectorAll("tr"));
        trs.sort(function (a, b) {
          var av = cellText(a, idx), bv = cellText(b, idx);
          if (numeric) {
            var an = parseFloat(av.replace(/[^0-9.,-]/g, "").replace(/\./g, "").replace(",", ".")) || 0;
            var bn = parseFloat(bv.replace(/[^0-9.,-]/g, "").replace(/\./g, "").replace(",", ".")) || 0;
            return asc ? an - bn : bn - an;
          }
          return asc ? av.localeCompare(bv, "pt") : bv.localeCompare(av, "pt");
        });
        trs.forEach(function (tr) { tbody.appendChild(tr); });
      });
    });
  }
})();
