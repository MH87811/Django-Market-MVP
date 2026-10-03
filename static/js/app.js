/* ==========================================================================
   app.js — shared UI behaviour. No data, no requests, no auth.
   Everything is driven by data-* attributes so the markup stays plain HTML:

   [data-panel-toggle="id"]   open/close the element #id (mobile menu, filters, sidebar)
   [data-dropdown]            wrapper;  [data-dropdown-toggle] button;  [data-dropdown-menu] menu
   [data-modal-open="id"]     open <dialog id>;  [data-modal-close] closes its dialog
   [data-toast="text"]        show a toast on click  (+ data-toast-type="success|error|info")
   [data-favorite]            favourite toggle (aria-pressed)
   [data-filter-tabs]         filter list items by data-status
   [data-toggle-password]     show / hide a password input
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Persian number helpers (shared with other scripts) ---------- */
  var faDigits = function (v) { return String(v).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; }); };
  var enDigits = function (v) {
    return String(v).replace(/[۰-۹]/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'.indexOf(d); })
                    .replace(/[٠-٩]/g, function (d) { return '٠١٢٣٤٥٦٧٨٩'.indexOf(d); })
                    .replace(/[٬,،\s]/g, '');
  };
  var formatPrice = function (n) { return faDigits(Math.round(n).toLocaleString('en-US')).replace(/,/g, '٬'); };
  var parseNumber = function (v) { return parseInt(enDigits(v), 10) || 0; };

  /* ---------- Icons ---------- */
  function renderIcons(root) {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
      $$('svg.lucide', root).forEach(function (svg) { svg.setAttribute('aria-hidden', 'true'); svg.setAttribute('focusable', 'false'); });
    }
  }

  /* ---------- Images must never break the layout ---------- */
  document.addEventListener('error', function (e) {
    var img = e.target;
    if (img && img.tagName === 'IMG') {
      var box = img.closest('.media') || img.parentElement;
      if (box) box.classList.add('is-broken');
    }
  }, true);
  $$('.media > img').forEach(function (img) {
    if (img.complete && img.naturalWidth === 0) img.closest('.media').classList.add('is-broken');
  });

  /* ---------- Toasts ---------- */
  var toastRegion = null;
  function toast(message, type) {
    type = type || 'success';
    if (!toastRegion) {
      toastRegion = document.createElement('div');
      toastRegion.className = 'toast-region';
      toastRegion.setAttribute('role', 'status');
      toastRegion.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastRegion);
    }
    var icons = { success: 'circle-check', error: 'circle-alert', info: 'info' };
    var el = document.createElement('div');
    el.className = 'toast toast--' + type;
    el.innerHTML = '<i data-lucide="' + (icons[type] || 'info') + '"></i><span></span>' +
      '<button type="button" class="toast-close" aria-label="بستن"><i data-lucide="x" class="icon-sm"></i></button>';
    el.querySelector('span').textContent = message;
    toastRegion.appendChild(el);
    renderIcons(el);
    var close = function () {
      el.classList.add('is-leaving');
      setTimeout(function () { el.remove(); }, 220);
    };
    el.querySelector('.toast-close').addEventListener('click', close);
    setTimeout(close, 3800);
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-toast]');
    if (t && !t.disabled) toast(t.getAttribute('data-toast'), t.getAttribute('data-toast-type') || 'success');
  });

  /* ---------- Panels (mobile menu, filter sheet, dashboard sidebar) ---------- */
  var overlay = document.createElement('div');
  overlay.className = 'panel-overlay';
  document.body.appendChild(overlay);
  var openPanel = null, lastTrigger = null;

  function setPanel(panel, open, trigger) {
    if (!panel) return;
    panel.classList.toggle('is-open', open);
    overlay.classList.toggle('is-visible', open);
    document.body.classList.toggle('has-panel-open', open);
    $$('[data-panel-toggle="' + panel.id + '"]').forEach(function (b) { b.setAttribute('aria-expanded', String(open)); });
    if (open) {
      openPanel = panel; lastTrigger = trigger || null;
      var focusable = panel.querySelector('[data-panel-close], a, button, input');
      if (focusable) setTimeout(function () { focusable.focus(); }, 60);
    } else {
      openPanel = null;
      if (lastTrigger) lastTrigger.focus();
    }
  }
  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-panel-toggle]');
    if (toggle) {
      var panel = document.getElementById(toggle.getAttribute('data-panel-toggle'));
      setPanel(panel, !panel.classList.contains('is-open'), toggle);
      return;
    }
    if (e.target.closest('[data-panel-close]') && openPanel) setPanel(openPanel, false);
  });
  overlay.addEventListener('click', function () { if (openPanel) setPanel(openPanel, false); });
  window.addEventListener('resize', function () {
    if (openPanel && window.innerWidth > 1024) setPanel(openPanel, false);
  });

  /* ---------- Dropdowns ---------- */
  function closeDropdowns(except) {
    $$('[data-dropdown]').forEach(function (d) {
      if (d === except) return;
      var m = d.querySelector('[data-dropdown-menu]'), b = d.querySelector('[data-dropdown-toggle]');
      if (m && !m.hidden) { m.hidden = true; if (b) b.setAttribute('aria-expanded', 'false'); }
    });
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-dropdown-toggle]');
    if (btn) {
      var wrap = btn.closest('[data-dropdown]');
      var menu = wrap.querySelector('[data-dropdown-menu]');
      var willOpen = menu.hidden;
      closeDropdowns(wrap);
      menu.hidden = !willOpen;
      btn.setAttribute('aria-expanded', String(willOpen));
      return;
    }
    if (!e.target.closest('[data-dropdown-menu]')) closeDropdowns();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var wasOpen = $$('[data-dropdown-menu]').some(function (m) { return !m.hidden; });
    closeDropdowns();
    if (openPanel) setPanel(openPanel, false);
    if (wasOpen) { var f = $('[data-dropdown-toggle][aria-expanded="false"]'); if (f) f.focus(); }
  });

  /* Mark all notifications as read */
  document.addEventListener('click', function (e) {
    if (!e.target.closest('[data-mark-all-read]')) return;
    $$('.notification-item.is-unread').forEach(function (n) { n.classList.replace('is-unread', 'is-read'); });
    $$('[data-notification-dot]').forEach(function (d) { d.hidden = true; });
    toast('همه اعلان‌ها خوانده شد', 'success');
  });

  /* ---------- Modals (native <dialog>) ---------- */
  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[data-modal-open]');
    if (opener) {
      var dlg = document.getElementById(opener.getAttribute('data-modal-open'));
      if (dlg && typeof dlg.showModal === 'function') dlg.showModal();
      return;
    }
    if (e.target.closest('[data-modal-close]')) {
      var d = e.target.closest('dialog');
      if (d) d.close();
      return;
    }
    if (e.target.tagName === 'DIALOG' && e.target.classList.contains('modal')) e.target.close(); // backdrop click
  });

  /* ---------- Favourite toggle ---------- */
  document.addEventListener('click', function (e) {
    var fav = e.target.closest('[data-favorite]');
    if (!fav) return;
    var on = fav.getAttribute('aria-pressed') !== 'true';
    fav.setAttribute('aria-pressed', String(on));
    fav.setAttribute('aria-label', on ? 'حذف از علاقه‌مندی‌ها' : 'افزودن به علاقه‌مندی‌ها');
    toast(on ? 'به علاقه‌مندی‌ها اضافه شد' : 'از علاقه‌مندی‌ها حذف شد', on ? 'success' : 'info');
  });

  /* ---------- Generic tabs ([data-tabs] > [role=tab], panels by aria-controls) ---------- */
  $$('[data-tabs]').forEach(function (tabs) {
    var buttons = $$('[role="tab"]', tabs);
    function select(btn) {
      buttons.forEach(function (b) {
        var on = b === btn;
        b.setAttribute('aria-selected', String(on));
        b.tabIndex = on ? 0 : -1;
        var p = document.getElementById(b.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
    }
    buttons.forEach(function (b, i) {
      b.addEventListener('click', function () { select(b); });
      b.addEventListener('keydown', function (e) {
        var dir = e.key === 'ArrowLeft' ? 1 : e.key === 'ArrowRight' ? -1 : 0; // RTL: left = next
        if (!dir) return;
        var n = buttons[(i + dir + buttons.length) % buttons.length];
        select(n); n.focus();
      });
    });
  });

  /* ---------- Filter tabs (orders list by status) ---------- */
  $$('[data-filter-tabs]').forEach(function (group) {
    var list = document.querySelector(group.getAttribute('data-filter-target'));
    var empty = document.querySelector(group.getAttribute('data-filter-empty'));
    if (!list) return;
    $$('button', group).forEach(function (btn) {
      btn.addEventListener('click', function () {
        $$('button', group).forEach(function (b) { b.setAttribute('aria-selected', String(b === btn)); });
        var f = btn.getAttribute('data-filter'), shown = 0;
        $$('[data-status]', list).forEach(function (item) {
          var ok = f === 'all' || item.getAttribute('data-status') === f;
          item.hidden = !ok; if (ok) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
        list.hidden = shown === 0;
      });
    });
  });

  /* ---------- Password visibility ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-toggle-password]');
    if (!b) return;
    var input = document.getElementById(b.getAttribute('data-toggle-password'));
    var show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    b.setAttribute('aria-label', show ? 'پنهان کردن گذرواژه' : 'نمایش گذرواژه');
    b.innerHTML = '<i data-lucide="' + (show ? 'eye-off' : 'eye') + '"></i>';
    renderIcons(b);
  });

  /* ---------- Visual-only form validation (no requests are sent) ---------- */
  $$('form[data-validate]').forEach(function (form) {
    var fields = $$('.input[required], .select[required], .textarea[required]', form);
    function check(input) {
      var group = input.closest('.form-group');
      var ok = input.checkValidity();
      var match = input.getAttribute('data-match');
      if (ok && match) ok = input.value === document.getElementById(match).value;
      group.classList.toggle('is-invalid', !ok);
      group.classList.toggle('is-valid', ok && input.value !== '');
      return ok;
    }
    fields.forEach(function (f) {
      f.addEventListener('blur', function () { if (f.value !== '') check(f); });
      f.addEventListener('input', function () { if (f.closest('.form-group').classList.contains('is-invalid')) check(f); });
    });
    form.addEventListener('submit', function (e) {
      var allOk = true;
      fields.forEach(function (f) { if (!check(f)) allOk = false; });
      if (!allOk) {
        e.preventDefault();
        var first = $('.is-invalid .input, .is-invalid .select', form);
        if (first) first.focus();
        toast('لطفاً خطاهای فرم را برطرف کنید', 'error');
      }
    });
  });

  /* ---------- Order-detail demo: preview other statuses with ?status=cancelled ---------- */
  var timeline = $('[data-order-timeline]');
  if (timeline) {
    var wanted = new URLSearchParams(window.location.search).get('status');
    var order = ['pending', 'paid', 'shipped', 'delivered'];
    if (wanted && (order.indexOf(wanted) > -1 || wanted === 'cancelled')) {
      var steps = $$('.order-step', timeline);
      var badge = $('[data-order-status-badge]');
      var labels = { pending: 'در انتظار پرداخت', paid: 'پرداخت شده', shipped: 'ارسال شده', delivered: 'تحویل داده شده', cancelled: 'لغو شده' };
      steps.forEach(function (s) { s.classList.remove('is-done', 'is-current', 'is-cancelled', 'is-upcoming'); });
      if (wanted === 'cancelled') {
        steps.forEach(function (s, i) { s.classList.add(i === 0 ? 'is-done' : 'is-upcoming'); });
        steps[1].classList.remove('is-upcoming'); steps[1].classList.add('is-cancelled');
        steps[1].querySelector('h3').textContent = 'لغو شده';
        steps[1].querySelector('p').textContent = 'سفارش لغو شد';
        steps[1].querySelector('[data-lucide], svg').outerHTML = '<i data-lucide="x"></i>';
        steps[2].hidden = true; steps[3].hidden = true;
        timeline.style.gridTemplateColumns = 'repeat(2, 1fr)';
      } else {
        var idx = order.indexOf(wanted);
        steps.forEach(function (s, i) { s.classList.add(i < idx ? 'is-done' : i === idx ? 'is-current' : 'is-upcoming'); });
      }
      if (badge) { badge.className = 'badge badge-dot status-' + wanted; badge.textContent = labels[wanted]; }
      var tracking = $('[data-tracking]');
      if (tracking && (wanted === 'pending' || wanted === 'paid' || wanted === 'cancelled')) tracking.textContent = 'هنوز صادر نشده';
      renderIcons(document);
    }
  }

  /* ---------- Expose a tiny API for the other scripts ---------- */
  window.Market = { $: $, $$: $$, toast: toast, renderIcons: renderIcons, faDigits: faDigits, enDigits: enDigits, formatPrice: formatPrice, parseNumber: parseNumber };

  document.addEventListener('DOMContentLoaded', function () { renderIcons(document); });
  if (document.readyState !== 'loading') renderIcons(document);
})();
