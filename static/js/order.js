/* Malto Maia \u2014 carrinho de encomenda (client-side) -> WhatsApp. */
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
    var fab = document.getElementById("order-fab");
    if (!ids.length) {
      el.innerHTML = '<p class="text-muted">' + esc(cfg.empty || "") + "</p>";
      totalRow.style.display = "none";
      note.style.display = "none";
      if (fab) fab.style.display = "none";
      return;
    }
    var html = "", total = 0, tbd = false;
    ids.forEach(function (id) {
      var it = cart[id];
      var sub = it.price != null ? fmt(it.price * it.qty) : (cfg.askPrice || "");
      if (it.price != null) total += it.price * it.qty; else tbd = true;
      html +=
        '<div class="cart-line"><span class="grow">' + esc(it.name) + "</span>" +
        '<span class="qty"><button type="button" data-act="dec" data-id="' + id + '">\u2212</button>' +
        "<b>" + it.qty + "</b>" +
        '<button type="button" data-act="inc" data-id="' + id + '">+</button></span>' +
        "<span>" + sub + "</span></div>";
    });
    el.innerHTML = html;
    document.getElementById("cart-total").textContent = fmt(total);
    totalRow.style.display = "flex";
    note.style.display = tbd ? "block" : "none";
    if (fab) { fab.style.display = "flex"; document.getElementById("fab-total").textContent = fmt(total); }
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

  function buildWaHref() {
    var ids = Object.keys(cart);
    if (!ids.length) return null;
    var d = new Date();
    var p2 = function (n) { return (n < 10 ? "0" : "") + n; };
    // codigo da comanda com SEGUNDOS (2 pedidos no mesmo minuto nao colidem)
    var code = "MM-" + p2(d.getDate()) + p2(d.getMonth() + 1) + "-" +
               p2(d.getHours()) + p2(d.getMinutes()) + p2(d.getSeconds());
    var when = p2(d.getDate()) + "/" + p2(d.getMonth() + 1) + " " +
               (cfg.waAt || "\u00b7") + " " + p2(d.getHours()) + ":" + p2(d.getMinutes());

    // Emojis em escape \u (arquivo ASCII puro) -- evita mojibake por charset no deploy.
    var DIV = "\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014";
    var L = [];
    L.push("\u2615 *MALTO MAIA*");
    L.push("_" + (cfg.waSubtitle || "") + "_");
    L.push("");
    L.push("\ud83e\uddfe *" + (cfg.waComanda || "Comanda") + ":* " + code);
    L.push("\ud83d\uddd3\ufe0f " + when);
    L.push(DIV);
    L.push("\ud83d\uded2 *" + (cfg.waItems || "") + "*");
    var total = 0, tbd = false;
    ids.forEach(function (id) {
      var it = cart[id];
      var sub = it.price != null ? fmt(it.price * it.qty) : (cfg.askPrice || "");
      if (it.price != null) total += it.price * it.qty; else tbd = true;
      L.push("\u2022 " + it.qty + "x " + it.name + " \u2014 *" + sub + "*");
    });
    L.push(DIV);
    L.push("\ud83d\udcb0 *" + (cfg.total || "Total") + ":* " + fmt(total) +
           (tbd ? " (+ " + (cfg.askPrice || "") + ")" : ""));
    var nome = (document.getElementById("cli-nome").value || "").trim();
    var obs = (document.getElementById("cli-obs").value || "").trim();
    if (nome || obs) L.push("");
    if (nome) L.push("\ud83d\ude4b *" + (cfg.waClient || "Cliente") + ":* " + nome);
    if (obs) L.push("\ud83d\udcdd *" + (cfg.notes || "Obs") + ":* " + obs);

    return "https://wa.me/" + cfg.wa + "?text=" + encodeURIComponent(L.join("\n"));
  }
  function onSend(e) {
    var href = buildWaHref();
    if (!href) { e.preventDefault(); return; }
    this.setAttribute("href", href);
  }
  document.getElementById("send-wa").addEventListener("click", onSend);
  var waFab = document.getElementById("send-wa-fab");
  if (waFab) waFab.addEventListener("click", onSend);

  render();
})();
