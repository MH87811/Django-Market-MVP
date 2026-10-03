/* ==========================================================================
   dashboard.js — vendor dashboard + product form behaviour (visual only).

   Chart:     [data-chart]  with  [data-chart-period] buttons
   Delete:    [data-modal-open="delete-modal"][data-product-name] on a table row
   Variants:  [data-variant-rows] + <template id="variant-row-template">
   Uploader:  input[data-image-input] → previews in [data-uploader]
   ========================================================================== */
(function () {
  'use strict';
  var M = window.Market, $ = M.$, $$ = M.$$;

  /* ---------- Lightweight CSS bar chart ---------- */
  var chart = $('[data-chart]');
  if (chart) {
    var datasets = {
      week: {
        labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'],
        values: [4.2, 6.8, 5.1, 8.9, 7.4, 11.2, 6.3], total: '۴۹٬۹۰۰٬۰۰۰'
      },
      month: {
        labels: ['هفته ۱', 'هفته ۲', 'هفته ۳', 'هفته ۴'],
        values: [38.5, 52.1, 47.6, 63.2], total: '۲۰۱٬۴۰۰٬۰۰۰'
      }
    };
    var bars = $('[data-chart-bars]', chart), labels = $('[data-chart-labels]', chart), total = $('[data-chart-total]', chart);

    var render = function (key) {
      var d = datasets[key], max = Math.max.apply(null, d.values);
      bars.innerHTML = ''; labels.innerHTML = '';
      d.values.forEach(function (v, i) {
        var col = document.createElement('div'); col.className = 'chart-col';
        var bar = document.createElement('button');
        bar.type = 'button';
        bar.className = 'chart-bar' + (v === max ? ' is-peak' : '');
        bar.style.setProperty('--h', Math.round((v / max) * 92) + '%');
        bar.setAttribute('aria-label', d.labels[i] + ': ' + M.faDigits(v.toFixed(1)) + ' میلیون تومان');
        var tip = document.createElement('span'); tip.className = 'chart-tip';
        tip.textContent = M.faDigits(v.toFixed(1)) + ' م';
        bar.appendChild(tip); col.appendChild(bar); bars.appendChild(col);
        var l = document.createElement('span'); l.textContent = d.labels[i]; labels.appendChild(l);
      });
      total.textContent = d.total;
    };
    $$('[data-chart-period]', chart).forEach(function (btn) {
      btn.addEventListener('click', function () {
        $$('[data-chart-period]', chart).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        render(btn.getAttribute('data-chart-period'));
      });
    });
    render('week');
  }

  /* ---------- Delete product confirmation ---------- */
  var deleteModal = document.getElementById('delete-modal');
  var pendingRow = null;
  if (deleteModal) {
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-modal-open="delete-modal"]');
      if (!trigger) return;
      pendingRow = trigger.closest('tr');
      var subject = $('[data-modal-subject]', deleteModal);
      if (subject) subject.textContent = trigger.getAttribute('data-product-name') || '';
    });
    var confirmBtn = $('[data-modal-confirm]', deleteModal);
    if (confirmBtn) {
      confirmBtn.addEventListener('click', function () {
        if (pendingRow) pendingRow.remove();
        pendingRow = null;
        deleteModal.close();
        M.toast('محصول حذف شد', 'success');
        if (!$('[data-product-rows] tr')) {
          var empty = $('[data-products-empty]'), wrap = $('[data-products-table]');
          if (empty) empty.hidden = false;
          if (wrap) wrap.hidden = true;
        }
      });
    }
  }

  /* ---------- Variant repeater ---------- */
  var rows = $('[data-variant-rows]');
  var tpl = document.getElementById('variant-row-template');
  if (rows && tpl) {
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-add-variant]')) {
        rows.appendChild(tpl.content.cloneNode(true));
        M.renderIcons(rows);
        var last = rows.lastElementChild; if (last) { var f = $('input', last); if (f) f.focus(); }
      }
      var rm = e.target.closest('[data-remove-variant]');
      if (rm) {
        rm.closest('.variant-row').remove();
        M.toast('گزینه حذف شد', 'info');
      }
    });
  }

  /* ---------- Image uploader preview ---------- */
  var input = $('[data-image-input]');
  var uploader = $('[data-uploader]');
  if (input && uploader) {
    input.addEventListener('change', function () {
      Array.prototype.forEach.call(input.files, function (file) {
        if (!/^image\//.test(file.type)) return;
        var tile = document.createElement('div');
        tile.className = 'upload-tile';
        var img = document.createElement('img');
        img.src = URL.createObjectURL(file); img.alt = file.name;
        img.style.cssText = 'width:100%;height:100%;object-fit:cover';
        var rm = document.createElement('button');
        rm.type = 'button'; rm.className = 'remove'; rm.setAttribute('aria-label', 'حذف تصویر');
        rm.innerHTML = '<i data-lucide="x" class="icon-sm"></i>';
        rm.addEventListener('click', function () { tile.remove(); });
        tile.appendChild(img); tile.appendChild(rm);
        uploader.insertBefore(tile, input.closest('.upload-add'));
        M.renderIcons(tile);
      });
      input.value = '';
    });
    uploader.addEventListener('click', function (e) {
      var rm = e.target.closest('.upload-tile .remove');
      if (rm) rm.closest('.upload-tile').remove();
    });
  }

  /* ---------- Product form: save buttons (visual feedback only) ---------- */
  $$('[data-save-draft]').forEach(function (b) {
    b.addEventListener('click', function () { M.toast('پیش‌نویس ذخیره شد', 'success'); });
  });
})();
