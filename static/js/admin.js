/* Malto Maia - admin: toggles AJAX, edicao no modal, tabela tipo Excel. */
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

  /* ----- Toggle sem reload (delegado: vale tambem p/ linhas recriadas) ----- */
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

  /* ----- Editar no box (modal) ----- */
  var modal = document.getElementById("edit-modal");
  var modalBody = document.getElementById("edit-modal-body");
  var editRow = null;

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    var link = e.target.closest(".js-edit");
    if (link && modal) {
      e.preventDefault();
      editRow = link.closest("tr");
      fetch(link.getAttribute("href"), { headers: ajaxHeaders() })
        .then(function (r) { return r.text(); })
        .then(function (html) { modalBody.innerHTML = html; modal.showModal(); });
      return;
    }
    if (modal && modal.open && (e.target === modal || e.target.closest("[data-close]"))) {
      modal.close();
    }
  });

  if (modal) {
    modal.addEventListener("submit", function (e) {
      var form = e.target;
      e.preventDefault();
      fetch(form.action, { method: "POST", headers: ajaxHeaders(csrf(form)), body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.ok) {
            if (data.reload) { location.reload(); return; }
            if (data.row && editRow) editRow.outerHTML = data.row;
            modal.close();
          } else if (data.form) {
            modalBody.innerHTML = data.form;
          }
        });
    });
  }

  /* ----- Tabela tipo Excel: busca instantanea + ordenar por coluna ----- */
  var table = document.querySelector(".adm-table");
  var search = document.querySelector('.adm-toolbar input[type="search"]');
  function cellText(tr, idx) { var td = tr.children[idx]; return td ? td.textContent.trim() : ""; }

  if (table && search) {
    var sform = search.closest("form");
    if (sform) sform.addEventListener("submit", function (e) { e.preventDefault(); });
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      [].forEach.call(table.querySelectorAll("tbody tr"), function (tr) {
        tr.style.display = (!q || tr.textContent.toLowerCase().indexOf(q) >= 0) ? "" : "none";
      });
    });
  }

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
