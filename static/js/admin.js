/* Malto Maia - admin: toggles sem reload (AJAX). Form com class="js-toggle". */
(function () {
  "use strict";

  function csrf(form) {
    var i = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return i ? i.value : "";
  }

  document.querySelectorAll("form.js-toggle").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var sw = form.querySelector(".switch");
      if (sw) sw.disabled = true;
      fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrf(form) },
        body: new FormData(form),
      })
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
        .catch(function () { form.submit(); }) // fallback: recarrega normal
        .then(function () { if (sw) sw.disabled = false; });
    });
  });

  /* ----- Tabela tipo Excel: busca instantanea + ordenar por coluna ----- */
  var table = document.querySelector(".adm-table");
  var search = document.querySelector('.adm-toolbar input[type="search"]');

  function cellText(tr, idx) { var td = tr.children[idx]; return td ? td.textContent.trim() : ""; }

  if (table && search) {
    var form = search.closest("form");
    if (form) form.addEventListener("submit", function (e) { e.preventDefault(); });
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
