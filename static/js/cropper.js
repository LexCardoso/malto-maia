/* Malto Maia - editor de foto no upload: recortar/ajustar + encolher (client-side).
   ASCII puro (WhiteNoise serve .js sem charset). Expoe window.MaltoCrop.open(file, cb). */
(function () {
  "use strict";
  var MAX_OUT = 1280; // maior lado do resultado

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function open(file, onConfirm) {
    if (!file || !/^image\//.test(file.type || "")) { onConfirm(file); return; }
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () { build(img, url, onConfirm); };
    img.onerror = function () { URL.revokeObjectURL(url); onConfirm(file); };
    img.src = url;
  }

  function build(img, url, onConfirm) {
    var overlay = el("div", "crop-ov");
    var modal = el("div", "crop-modal", overlay);
    el("div", "crop-head", modal).textContent = "Ajuste a foto";
    var stage = el("div", "crop-stage", modal);
    var imgEl = el("img", "crop-img", stage);
    imgEl.src = url;
    var box = el("div", "crop-box", stage);
    ["h0", "h1", "h2", "h3"].forEach(function (h) { el("span", "crop-h " + h, box); });
    el("div", "crop-hint", modal).textContent =
      "Arraste pra mover, puxe os cantos pra recortar. Ou use a foto inteira.";
    var actions = el("div", "crop-actions", modal);
    var btnCancel = el("button", "btn btn-ghost btn-sm", actions);
    btnCancel.type = "button"; btnCancel.textContent = "Cancelar";
    var btnFull = el("button", "btn btn-ghost btn-sm", actions);
    btnFull.type = "button"; btnFull.textContent = "Foto inteira";
    var btnUse = el("button", "btn btn-primary btn-sm", actions);
    btnUse.type = "button"; btnUse.textContent = "Recortar e usar";
    document.body.appendChild(overlay);

    var dispW, dispH;
    function layout() {
      var maxW = Math.min(window.innerWidth - 44, 720);
      var maxH = window.innerHeight - 210;
      var r = Math.min(maxW / img.naturalWidth, maxH / img.naturalHeight, 1);
      dispW = Math.max(60, Math.round(img.naturalWidth * r));
      dispH = Math.max(60, Math.round(img.naturalHeight * r));
      stage.style.width = dispW + "px";
      stage.style.height = dispH + "px";
    }
    layout();
    var crop = { x: 0, y: 0, w: dispW, h: dispH };
    function draw() {
      box.style.left = crop.x + "px"; box.style.top = crop.y + "px";
      box.style.width = crop.w + "px"; box.style.height = crop.h + "px";
    }
    draw();

    var drag = null;
    stage.addEventListener("pointerdown", function (e) {
      var cls = "" + (e.target.className || "");
      var isHandle = cls.indexOf("crop-h") >= 0;
      if (!isHandle && e.target !== box) return;
      var rect = stage.getBoundingClientRect();
      drag = {
        sx: e.clientX - rect.left, sy: e.clientY - rect.top,
        c: { x: crop.x, y: crop.y, w: crop.w, h: crop.h },
        handle: isHandle ? cls : null,
      };
      try { stage.setPointerCapture(e.pointerId); } catch (err) {}
      e.preventDefault();
    });
    stage.addEventListener("pointermove", function (e) {
      if (!drag) return;
      var rect = stage.getBoundingClientRect();
      var dx = (e.clientX - rect.left) - drag.sx, dy = (e.clientY - rect.top) - drag.sy, c = drag.c;
      if (!drag.handle) {
        crop.x = clamp(c.x + dx, 0, dispW - c.w);
        crop.y = clamp(c.y + dy, 0, dispH - c.h);
      } else {
        var left = drag.handle.indexOf("h0") >= 0 || drag.handle.indexOf("h3") >= 0;
        var top = drag.handle.indexOf("h0") >= 0 || drag.handle.indexOf("h1") >= 0;
        if (left) { var nx = clamp(c.x + dx, 0, c.x + c.w - 48); crop.x = nx; crop.w = c.x + c.w - nx; }
        else { crop.w = clamp(c.w + dx, 48, dispW - c.x); }
        if (top) { var ny = clamp(c.y + dy, 0, c.y + c.h - 48); crop.y = ny; crop.h = c.y + c.h - ny; }
        else { crop.h = clamp(c.h + dy, 48, dispH - c.y); }
      }
      draw();
    });
    stage.addEventListener("pointerup", function () { drag = null; });
    stage.addEventListener("pointercancel", function () { drag = null; });

    function close() {
      URL.revokeObjectURL(url);
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    }
    function finish(useFull) {
      var scale = img.naturalWidth / dispW;
      var sx = useFull ? 0 : crop.x * scale, sy = useFull ? 0 : crop.y * scale;
      var sw = useFull ? img.naturalWidth : crop.w * scale;
      var sh = useFull ? img.naturalHeight : crop.h * scale;
      var r = Math.min(MAX_OUT / sw, MAX_OUT / sh, 1);
      var ow = Math.max(1, Math.round(sw * r)), oh = Math.max(1, Math.round(sh * r));
      var cv = document.createElement("canvas");
      cv.width = ow; cv.height = oh;
      cv.getContext("2d").drawImage(img, sx, sy, sw, sh, 0, 0, ow, oh);
      cv.toBlob(function (blob) { close(); onConfirm(blob || null); }, "image/jpeg", 0.85);
    }
    btnCancel.addEventListener("click", function () { close(); onConfirm(null); });
    btnFull.addEventListener("click", function () { finish(true); });
    btnUse.addEventListener("click", function () { finish(false); });
  }

  window.MaltoCrop = { open: open };
})();
