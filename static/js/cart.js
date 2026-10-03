/* ==========================================================================
   cart.js — quantity controls + cart totals (visual only, nothing is stored).

   Quantity:  .quantity > [data-qty-minus] [data-qty-input] [data-qty-plus]
   Cart:      [data-cart] > .cart-seller[data-shipping] > .cart-item[data-unit-price]
   Header:    [data-cart-count]  badge, updated by add-to-cart buttons
   ========================================================================== */
(function () {
  'use strict';
  var M = window.Market, $ = M.$, $$ = M.$$;

  /* ---------- Quantity control (used on product detail and cart) ---------- */
  function clamp(input) {
    var min = parseInt(input.min || '1', 10), max = parseInt(input.max || '99', 10);
    var v = M.parseNumber(input.value);
    if (v < min) v = min;
    if (v > max) v = max;
    input.value = M.faDigits(v);
    var wrap = input.closest('.quantity');
    var minus = $('[data-qty-minus]', wrap), plus = $('[data-qty-plus]', wrap);
    if (minus) minus.disabled = v <= min;
    if (plus) plus.disabled = v >= max;
    return v;
  }
  function stepQty(btn, delta) {
    var input = $('[data-qty-input]', btn.closest('.quantity'));
    input.value = M.parseNumber(input.value) + delta;
    clamp(input);
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  document.addEventListener('click', function (e) {
    var minus = e.target.closest('[data-qty-minus]'), plus = e.target.closest('[data-qty-plus]');
    if (minus) stepQty(minus, -1);
    if (plus) stepQty(plus, 1);
  });
  document.addEventListener('change', function (e) {
    if (e.target.matches('[data-qty-input]')) clamp(e.target);
  });
  $$('[data-qty-input]').forEach(clamp);

  /* ---------- Header cart badge ---------- */
  function setCartCount(n) {
    $$('[data-cart-count]').forEach(function (el) {
      el.textContent = M.faDigits(n);
      el.hidden = n <= 0;
    });
  }
  document.addEventListener('click', function (e) {
    var add = e.target.closest('[data-add-to-cart]');
    if (!add || add.disabled) return;
    var badge = $('[data-cart-count]');
    var current = badge ? M.parseNumber(badge.textContent) : 0;
    var qty = $('[data-qty-input]');
    setCartCount(current + (qty ? M.parseNumber(qty.value) : 1));
  });

  /* ---------- Cart page totals ---------- */
  var cart = $('[data-cart]');
  if (!cart) return;

  var emptyState = $('[data-cart-empty]');
  var contents = $$('[data-cart-content]');

  function recalc() {
    var grandSub = 0, grandShip = 0, items = 0;
    $$('.cart-seller', cart).forEach(function (seller) {
      var sub = 0, count = 0;
      $$('.cart-item', seller).forEach(function (item) {
        var unit = parseInt(item.getAttribute('data-unit-price'), 10);
        var qty = M.parseNumber($('[data-qty-input]', item).value);
        var total = unit * qty;
        $('[data-item-total]', item).firstChild.nodeValue = M.formatPrice(total) + ' ';
        sub += total; count += qty;
      });
      var threshold = parseInt(seller.getAttribute('data-free-shipping') || '0', 10);
      var ship = parseInt(seller.getAttribute('data-shipping') || '0', 10);
      if (threshold && sub >= threshold) ship = 0;
      var subEl = $('[data-seller-subtotal]', seller);
      if (subEl) subEl.firstChild.nodeValue = M.formatPrice(sub) + ' ';
      var shipEl = $('[data-seller-shipping]', seller);
      if (shipEl) shipEl.textContent = ship === 0 ? 'ارسال رایگان' : 'هزینه ارسال: ' + M.formatPrice(ship) + ' تومان';
      var sumRow = document.querySelector('[data-summary-seller="' + seller.id + '"] strong');
      if (sumRow) sumRow.textContent = M.formatPrice(sub) + ' تومان';
      grandSub += sub; grandShip += ship; items += count;
    });

    $$('[data-summary-subtotal]').forEach(function (el) { el.textContent = M.formatPrice(grandSub) + ' تومان'; });
    $$('[data-summary-shipping]').forEach(function (el) { el.textContent = grandShip === 0 ? 'رایگان' : M.formatPrice(grandShip) + ' تومان'; });
    $$('[data-summary-total]').forEach(function (el) { el.textContent = M.formatPrice(grandSub + grandShip) + ' تومان'; });
    $$('[data-summary-count]').forEach(function (el) { el.textContent = M.faDigits(items); });
    setCartCount(items);
  }

  cart.addEventListener('change', function (e) { if (e.target.matches('[data-qty-input]')) recalc(); });

  cart.addEventListener('click', function (e) {
    var rm = e.target.closest('[data-remove-item]');
    if (!rm) return;
    var item = rm.closest('.cart-item'), seller = rm.closest('.cart-seller');
    item.remove();
    if (!$('.cart-item', seller)) {
      var row = document.querySelector('[data-summary-seller="' + seller.id + '"]');
      if (row) row.remove();
      seller.remove();
    }
    M.toast('محصول از سبد خرید حذف شد', 'info');
    if (!$('.cart-seller', cart)) {
      contents.forEach(function (c) { c.hidden = true; });
      if (emptyState) emptyState.hidden = false;
      document.body.classList.remove('has-summary-bar');
      setCartCount(0);
    } else {
      recalc();
    }
  });

  document.body.classList.add('has-summary-bar');
  recalc();
})();
