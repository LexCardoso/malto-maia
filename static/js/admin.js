/* Malto Maia - admin: toggles AJAX, edicao IN-LINE na linha, buscar/filtrar/ordenar. */
(function () {
  "use strict";

  function csrf(form) {
    var i = form.querySelector('input[name="csrfmiddlewaretoken"]');
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
    fetch(form.action, { method: "POST", headers: ajaxHeaders(csrf(form)), body: new FormData(form) })
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

  /* ----- Editar NA LINHA (in-place; a linha fica mais escura) ----- */
  var editingRow = null, editingHTML = "";

  function closeEditor(restore) {
    if (!editingRow) return;
    if (restore) editingRow.outerHTML = editingHTML;
    editingRow = null; editingHTML = "";
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    var link = e.target.closest(".js-edit");
    if (link) {
      e.preventDefault();
      var tr = link.closest("tr");
      if (editingRow && editingRow !== tr) closeEditor(true);
      editingRow = tr;
      editingHTML = tr.outerHTML;
      var cols = tr.children.length;
      fetch(link.getAttribute("href"), { headers: ajaxHeaders() })
        .then(function (r) { return r.text(); })
        .then(function (html) {
          tr.classList.add("editing");
          tr.innerHTML = '<td colspan="' + cols + '" class="edit-cell">' + html + "</td>";
          var f = tr.querySelector("input, select, textarea");
          if (f) f.focus();
        });
      return;
    }
    if (e.target.closest("[data-close]") && editingRow) { e.preventDefault(); closeEditor(true); }
  });

  document.addEventListener("submit", function (e) {
    var form = e.target.closest ? e.target.closest(".adm-edit-form") : null;
    if (!form) return;
    e.preventDefault();
    fetch(form.action, { method: "POST", headers: ajaxHeaders(csrf(form)), body: new FormData(form) })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok) {
          if (data.reload) { location.reload(); return; }
          if (data.row && editingRow) { editingRow.outerHTML = data.row; editingRow = null; editingHTML = ""; }
        } else if (data.form && editingRow) {
          var cell = editingRow.querySelector(".edit-cell");
          if (cell) cell.innerHTML = data.form;
        }
      });
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
