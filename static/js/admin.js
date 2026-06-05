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
})();
