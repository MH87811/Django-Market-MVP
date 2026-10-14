# بازارچه — Static frontend prototype

Open `index.html` in a browser. No build step. Pure HTML + CSS + vanilla JS.

- `css/style.css`      tokens (CSS variables), base, buttons, forms, navbar, footer
- `css/components.css` product card, cart, orders, dashboard, modal, toast, states…
- `css/responsive.css` breakpoints 1280 / 1024 / 768 / 480
- `js/app.js`          panels, dropdowns, dialogs, toasts, tabs, favourites, validation UI
- `js/products.js`     gallery, variant → price/stock, sort sheet, filter chips
- `js/cart.js`         quantity control, cart totals per seller
- `js/dashboard.js`    CSS bar chart, delete dialog, variant repeater, image preview

Icons (Lucide) and the Vazirmatn font load from CDNs; product photos are picsum placeholders.
Layout never depends on them (image boxes have tinted fallbacks).
Behaviour hooks are `data-*` attributes, so markup stays plain and template-friendly.
