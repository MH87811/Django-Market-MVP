/* ==========================================================================
   products.js — product listing + product detail UI behaviour.

   Gallery:   [data-gallery] > [data-gallery-main] img,  [data-gallery-thumb][data-src]
   Variants:  [data-variants] contains radio inputs with
              data-price-modifier (toman) and data-stock (units)
   Price:     [data-product-price][data-base-price]  →  [data-price-current] / [data-price-old]
   Sort:      select[data-sort-select]  ⇄  dialog#sort-modal radio[name=sort]
   ========================================================================== */
(function () {
  'use strict';
  var M = window.Market, $ = M.$, $$ = M.$$;

  /* ---------- Gallery ---------- */
  $$('[data-gallery]').forEach(function (g) {
    var main = $('[data-gallery-main] img', g);
    var thumbs = $$('[data-gallery-thumb]', g);
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () {
        thumbs.forEach(function (x) { x.setAttribute('aria-current', String(x === t)); });
        var box = main.closest('.media');
        box.classList.remove('is-broken');
        main.src = t.getAttribute('data-src');
        main.alt = t.getAttribute('data-alt') || main.alt;
      });
    });
  });

  /* ---------- Variants: price + stock react to the selection ---------- */
  var variantRoot = $('[data-variants]');
  var priceBox = $('[data-product-price]');
  if (variantRoot && priceBox) {
    var base = parseInt(priceBox.getAttribute('data-base-price'), 10);
    var oldBase = parseInt(priceBox.getAttribute('data-old-price') || '0', 10);
    var current = $('[data-price-current]', priceBox);
    var old = $('[data-price-old]', priceBox);
    var stockEl = $('[data-stock-label]');
    var addBtns = $$('[data-add-to-cart], [data-buy-now]');
    var qtyInput = $('[data-qty-input]');
    var selectedLabels = $$('[data-selected-label]');

    function update() {
      var modifier = 0, stock = Infinity;
      $$('input[type="radio"]:checked', variantRoot).forEach(function (r) {
        modifier += parseInt(r.getAttribute('data-price-modifier') || '0', 10);
        stock = Math.min(stock, parseInt(r.getAttribute('data-stock') || '0', 10));
        var lbl = $('[data-selected-label="' + r.name + '"]');
        if (lbl) lbl.textContent = r.value;
      });
      if (stock === Infinity) stock = 99;

      current.firstChild.nodeValue = M.formatPrice(base + modifier) + ' ';
      if (old && oldBase) old.textContent = M.formatPrice(oldBase + modifier);

      stockEl.classList.remove('stock-in', 'stock-low', 'stock-out');
      if (stock <= 0) { stockEl.classList.add('stock-out'); stockEl.textContent = 'ناموجود'; }
      else if (stock <= 5) { stockEl.classList.add('stock-low'); stockEl.textContent = 'فقط ' + M.faDigits(stock) + ' عدد در انبار'; }
      else { stockEl.classList.add('stock-in'); stockEl.textContent = 'موجود در انبار'; }

      addBtns.forEach(function (b) { b.disabled = stock <= 0; });
      if (qtyInput) {
        qtyInput.max = Math.max(stock, 1);
        qtyInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    variantRoot.addEventListener('change', update);
    update();
  }

  /* ---------- Sort: mobile sheet ⇄ desktop select ---------- */
  var select = $('[data-sort-select]');
  var sortModal = document.getElementById('sort-modal');
  if (sortModal) {
    sortModal.addEventListener('change', function (e) {
      if (e.target.name !== 'sort') return;
      if (select) select.value = e.target.value;
      var label = $('[data-sort-label]');
      if (label) label.textContent = e.target.parentElement.textContent.trim();
      sortModal.close();
      M.toast('مرتب‌سازی اعمال شد', 'info');
    });
  }
  if (select) {
    select.addEventListener('change', function () {
      M.toast('مرتب‌سازی اعمال شد', 'info');
      var r = sortModal && $('input[value="' + select.value + '"]', sortModal);
      if (r) r.checked = true;
    });
  }

  /* ---------- Active filter chips ---------- */
  document.addEventListener('click', function (e) {
    var rm = e.target.closest('[data-chip-remove]');
    if (!rm) return;
    var chip = rm.closest('.chip');
    var target = chip.getAttribute('data-filter-id');
    if (target) { var cb = document.getElementById(target); if (cb) cb.checked = false; }
    chip.remove();
  });

  /* ---------- Clear all filters ---------- */
  var clear = $('[data-clear-filters]');
  if (clear) {
    clear.addEventListener('click', function () {
      $$('.filters input[type="checkbox"]').forEach(function (c) { c.checked = false; });
      $$('.filters input[type="number"]').forEach(function (n) { n.value = ''; });
      $$('[data-active-filters] .chip').forEach(function (c) { c.remove(); });
      M.toast('فیلترها پاک شد', 'info');
    });
  }
  var apply = $('[data-apply-filters]');
  if (apply) {
    apply.addEventListener('click', function () {
      var panel = apply.closest('.filters');
      var closeBtn = $('[data-panel-close]', panel);
      if (closeBtn) closeBtn.click();
      M.toast('فیلترها اعمال شد', 'info');
    });
  }
})();
