/* Malto Maia — carrinho de encomenda (client-side) -> WhatsApp. */
(function () {
  "use strict";
  var cfg = window.MALTO_ORDER || {};
  var cart = {}; // id -> { name, price(Number|null), qty }

  function fmt(n) {
    var s = n.toFixed(2).split(".");
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return "R$ " + s[0] + "," + s[1];
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function render() {
    var el = document.getElementById("cart");
    var ids = Object.keys(cart);
    var totalRow = document.getElementById("cart-total-row");
    var note = document.getElementById("cart-note");
    if (!ids.length) {
      el.innerHTML = '<p class="text-muted">' + esc(cfg.empty || "") + "</p>";
      totalRow.style.display = "none";
      note.style.display = "none";
      return;
    }
    var html = "", total = 0, tbd = false;
    ids.forEach(function (id) {
      var it = cart[id];
      var sub = it.price != null ? fmt(it.price * it.qty) : (cfg.askPrice || "");
      if (it.price != null) total += it.price * it.qty; else tbd = true;
      html +=
        '<div class="cart-line"><span class="grow">' + esc(it.name) + "</span>" +
        '<span class="qty"><button type="button" data-act="dec" data-id="' + id + '">−</button>' +
        "<b>" + it.qty + "</b>" +
        '<button type="button" data-act="inc" data-id="' + id + '">+</button></span>' +
        "<span>" + sub + "</span></div>";
    });
    el.innerHTML = html;
    document.getElementById("cart-total").textContent = fmt(total);
    totalRow.style.display = "flex";
    note.style.display = tbd ? "block" : "none";
  }

  function add(id, name, price) {
    if (cart[id]) cart[id].qty++;
    else cart[id] = { name: name, price: price, qty: 1 };
    render();
  }

  document.querySelectorAll(".js-add").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var p = btn.getAttribute("data-price");
      add(btn.getAttribute("data-id"), btn.getAttribute("data-name"), p ? parseFloat(p) : null);
    });
  });

  document.getElementById("cart").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-act]");
    if (!b) return;
    var id = b.getAttribute("data-id");
    if (!cart[id]) return;
    if (b.getAttribute("data-act") === "inc") cart[id].qty++;
    else if (--cart[id].qty <= 0) delete cart[id];
    render();
  });

  document.getElementById("clear-cart").addEventListener("click", function () {
    cart = {};
    render();
  });

  document.getElementById("send-wa").addEventListener("click", function (e) {
    var ids = Object.keys(cart);
    if (!ids.length) {
      e.preventDefault();
      return;
    }
    var lines = [cfg.waHeader || "", ""];
    var total = 0, tbd = false;
    ids.forEach(function (id) {
      var it = cart[id];
      var sub = it.price != null ? fmt(it.price * it.qty) : (cfg.askPrice || "");
      if (it.price != null) total += it.price * it.qty; else tbd = true;
      lines.push("• " + it.qty + "x " + it.name + " — " + sub);
    });
    lines.push("");
    lines.push((cfg.total || "Total") + ": " + fmt(total) + (tbd ? " (+ a definir)" : ""));
    var nome = (document.getElementById("cli-nome").value || "").trim();
    var obs = (document.getElementById("cli-obs").value || "").trim();
    if (nome) lines.push((cfg.name || "Nome") + ": " + nome);
    if (obs) lines.push((cfg.notes || "Obs") + ": " + obs);
    this.setAttribute(
      "href",
      "https://wa.me/" + cfg.wa + "?text=" + encodeURIComponent(lines.join("\n"))
    );
  });

  render();
})();
