const app = {
    cart: [],
    products: [],
    searchQuery: '',
    currentPage: 1,
    itemsPerPage: 12,
    currentOrderContext: null,

    init: function() {
        // Load products if on attendant screen
        if (document.getElementById('product-grid')) {
            this.fetchProducts();
        }
    },

    // --- Utilities ---
    formatMoney: (amount) => `Tsh ${Math.round(parseFloat(amount)).toLocaleString('en-US')}`,
    
    showModal: (id) => document.getElementById(id).classList.add('active'),
    closeModal: (id) => document.getElementById(id).classList.remove('active'),

    // --- Attendant Logic ---
    fetchProducts: async function() {
        try {
            const res = await fetch('/api/products/');
            const data = await res.json();
            this.products = data.products;
            this.renderProductGrid();
        } catch (e) {
            console.error('Error fetching products:', e);
        }
    },

    filterProducts: function(query) {
        this.searchQuery = query.toLowerCase().trim();
        this.currentPage = 1; // Reset to first page on new search
        this.renderProductGrid();
    },

    renderProductGrid: function() {
        const grid = document.getElementById('product-grid');
        if (!grid) return;

        grid.innerHTML = '';
        const filtered = this.products.filter(p => p.name.toLowerCase().includes(this.searchQuery));

        const countSpan = document.getElementById('product-count');
        if (countSpan) {
            countSpan.textContent = `${filtered.length} ya ${this.products.length} bidhaa`;
        }

        if (filtered.length === 0) {
            grid.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 2rem;">Hakuna bidhaa inayofanana na utafutaji wako.</p>';
            this.renderPaginationControls(0);
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedItems = filtered.slice(startIndex, endIndex);

        paginatedItems.forEach(p => {
            const div = document.createElement('div');
            div.className = 'product-card';
            div.onclick = () => this.addToCart(p);
            div.innerHTML = `
                <h3>${p.name}</h3>
                <div class="price">${this.formatMoney(p.price)}</div>
                <div class="stock" style="${p.stock_quantity < 10 ? 'color: var(--danger); font-weight: bold;' : ''}">Zipo: ${p.stock_quantity}</div>
            `;
            grid.appendChild(div);
        });
        
        this.renderPaginationControls(filtered.length);
    },

    changePage: function(delta) {
        this.currentPage += delta;
        this.renderProductGrid();
    },

    renderPaginationControls: function(totalItems) {
        const container = document.getElementById('pagination-controls');
        if (!container) return;
        
        if (totalItems <= this.itemsPerPage) {
            container.innerHTML = '';
            return;
        }
        
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        
        container.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                <button class="btn" style="background: var(--bg-card);" onclick="app.changePage(-1)" ${this.currentPage === 1 ? 'disabled' : ''}>Nyuma</button>
                <span style="color: var(--text-muted); font-size: 0.9rem;">Ukurasa ${this.currentPage} wa ${totalPages}</span>
                <button class="btn" style="background: var(--bg-card);" onclick="app.changePage(1)" ${this.currentPage === totalPages ? 'disabled' : ''}>Mbele</button>
            </div>
        `;
    },

    addToCart: function(product) {
        const existing = this.cart.find(i => i.product_id === product.id);
        if (existing) {
            existing.quantity++;
        } else {
            this.cart.push({ product_id: product.id, name: product.name, price: product.price, quantity: 1 });
        }
        this.renderCart();
    },

    removeFromCart: function(productId) {
        this.cart = this.cart.filter(i => i.product_id !== productId);
        this.renderCart();
    },

    updateCartQuantity: function(productId, change) {
        const item = this.cart.find(i => i.product_id === productId);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                this.renderCart();
            }
        }
    },

    renderCart: function() {
        const cartDiv = document.getElementById('cart-items');
        const totalDiv = document.getElementById('grand-total');
        
        if (this.cart.length === 0) {
            cartDiv.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Kikapu kiko wazi</p>';
            totalDiv.textContent = 'Tsh 0';
            return;
        }

        cartDiv.innerHTML = '';
        let grandTotal = 0;

        this.cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            grandTotal += itemTotal;
            
            const div = document.createElement('div');
            div.style.display = 'flex';
            div.style.justifyContent = 'space-between';
            div.style.alignItems = 'center';
            div.style.marginBottom = '0.5rem';
            div.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <button onclick="app.updateCartQuantity(${item.product_id}, -1)" style="background:var(--glass-border); border:none; color:white; padding:2px 8px; border-radius:4px; cursor:pointer;">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="app.updateCartQuantity(${item.product_id}, 1)" style="background:var(--glass-border); border:none; color:white; padding:2px 8px; border-radius:4px; cursor:pointer;">+</button>
                    <span style="margin-left: 0.5rem;">${item.name}</span>
                </div>
                <span>${this.formatMoney(itemTotal)} <button onclick="app.removeFromCart(${item.product_id})" style="background:none;border:none;color:var(--danger);cursor:pointer;margin-left:5px;font-size:1.2rem;">&times;</button></span>
            `;
            cartDiv.appendChild(div);
        });

        totalDiv.textContent = this.formatMoney(grandTotal);
    },

    sendToCashier: async function() {
        const name = document.getElementById('customer_name').value.trim();
        if (!name) return alert('Tafadhali ingiza jina la mteja.');
        if (this.cart.length === 0) return alert('Kikapu kiko wazi.');

        try {
            const res = await fetch('/api/order/create/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer_name: name, items: this.cart })
            });
            const data = await res.json();
            if (data.success) {
                alert('Oda imetumwa kwa Keshia!');
                this.cart = [];
                document.getElementById('customer_name').value = '';
                this.renderCart();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (e) {
            alert('Network error.');
        }
    },

    // --- Cashier Logic ---
    fetchPendingOrders: async function() {
        if (!document.getElementById('pending-orders-list')) return;
        try {
            const res = await fetch('/api/orders/pending/');
            const data = await res.json();
            const list = document.getElementById('pending-orders-list');
            list.innerHTML = '';
            
            if (data.orders.length === 0) {
                list.innerHTML = '<p style="color: var(--text-muted);">Hakuna oda zinazosubiri.</p>';
                return;
            }

            data.orders.forEach(o => {
                const li = document.createElement('li');
                li.className = 'queue-item';
                li.innerHTML = `
                    <div>
                        <strong style="font-size: 1.2rem;">${o.customer_name}</strong>
                        <div style="color: var(--text-muted); font-size: 0.9rem;">Order #${o.id} - ${o.items.length} items</div>
                    </div>
                    <button class="btn btn-primary" onclick='app.openPaymentModal(${JSON.stringify(o)})'>Review</button>
                `;
                list.appendChild(li);
            });
        } catch (e) {
            console.error('Fetch pending error:', e);
        }
    },

    fetchCashierPaidOrders: async function() {
        if (!document.getElementById('cashier-paid-orders-list')) return;
        try {
            const res = await fetch('/api/orders/cashier_paid/');
            const data = await res.json();
            const list = document.getElementById('cashier-paid-orders-list');
            list.innerHTML = '';
            
            if (data.orders.length === 0) {
                list.innerHTML = '<p style="color: var(--text-muted);">Hakuna oda zilizolipiwa.</p>';
                return;
            }

            data.orders.forEach(o => {
                const li = document.createElement('li');
                li.className = 'queue-item';
                li.innerHTML = `
                    <div>
                        <strong style="font-size: 1.2rem;">${o.customer_name}</strong>
                        <div style="color: var(--text-muted); font-size: 0.9rem;">Order #${o.id} - ${o.items.length} items</div>
                    </div>
                    <button class="btn btn-primary" onclick='app.openPaymentModal(${JSON.stringify(o)}, true)'>Chapisha Tena</button>
                `;
                list.appendChild(li);
            });
        } catch (e) {
            console.error('Fetch paid error:', e);
        }
    },

    openPaymentModal: function(order, isReprint = false) {
        this.currentOrderContext = order;
        document.getElementById('modal-customer-name').textContent = order.customer_name;
        document.getElementById('modal-grand-total').textContent = this.formatMoney(order.grand_total);
        
        const itemsDiv = document.getElementById('modal-order-items');
        itemsDiv.innerHTML = order.items.map(i => `<div>${i.qty}x ${i.name} - ${this.formatMoney(i.price * i.qty)}</div>`).join('');
        
        const btn = document.getElementById('btn-mark-paid');
        if (isReprint) {
            btn.textContent = 'Chapisha Risiti';
            btn.onclick = () => {
                this.closeModal('payment-modal');
                this.showReceipt(order.token);
            };
        } else {
            btn.textContent = '[Imelipiwa / Kamilisha]';
            btn.onclick = () => this.processPayment(order.id);
        }
        
        this.showModal('payment-modal');
    },

    processPayment: async function(orderId) {
        try {
            const res = await fetch(`/api/order/${orderId}/pay/`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.closeModal('payment-modal');
                this.showReceipt(data.token);
            } else {
                alert('Payment failed: ' + data.error);
            }
        } catch (e) {
            alert('Network error');
        }
    },

    showReceipt: function(token) {
        const order = this.currentOrderContext;
        document.getElementById('receipt-date').textContent = new Date().toLocaleString();
        
        const itemsContainer = document.getElementById('receipt-items-container');
        itemsContainer.innerHTML = order.items.map(i => `
            <div class="receipt-item">
                <span>${i.qty}x ${i.name}</span>
                <span>${this.formatMoney(i.price * i.qty)}</span>
            </div>
        `).join('');
        
        document.getElementById('receipt-grand-total').textContent = this.formatMoney(order.grand_total);
        document.getElementById('receipt-token-display').textContent = token;
        
        this.showModal('receipt-modal');
    },

    closeReceiptAndRefresh: function() {
        this.closeModal('receipt-modal');
        this.fetchPendingOrders();
        if (this.fetchCashierPaidOrders) this.fetchCashierPaidOrders();
    },

    // --- Dispatcher Logic ---
    fetchPaidOrders: async function() {
        if (!document.getElementById('paid-orders-list')) return;
        try {
            const res = await fetch('/api/orders/paid/');
            const data = await res.json();
            const list = document.getElementById('paid-orders-list');
            list.innerHTML = '';
            
            if (data.orders.length === 0) {
                list.innerHTML = '<p style="color: var(--text-muted);">Foleni iko wazi.</p>';
                return;
            }

            data.orders.forEach(o => {
                const li = document.createElement('li');
                li.className = 'queue-item';
                li.innerHTML = `
                    <div>
                        <strong style="font-size: 1.2rem;">${o.customer_name}</strong>
                        <div style="color: var(--text-muted); font-size: 0.9rem;">Order #${o.id}</div>
                    </div>
                    <button class="btn btn-primary" onclick='app.openTokenModal(${JSON.stringify(o)})'>Select</button>
                `;
                list.appendChild(li);
            });
        } catch (e) {
            console.error('Fetch paid error:', e);
        }
    },

    openTokenModal: function(order) {
        this.currentOrderContext = order;
        document.getElementById('token-modal-customer').textContent = order.customer_name;
        document.getElementById('token-input').value = '';
        document.getElementById('token-error').style.display = 'none';
        
        const btn = document.getElementById('btn-verify-token');
        btn.onclick = () => this.verifyToken();
        
        this.showModal('token-modal');
    },

    verifyToken: async function() {
        const token = document.getElementById('token-input').value.trim();
        const order = this.currentOrderContext;
        
        // Optimistic / Backend verification
        // Since we are required to securely check against backend:
        try {
            const res = await fetch(`/api/order/${order.id}/dispatch/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
            });
            const data = await res.json();
            
            if (data.success) {
                this.closeModal('token-modal');
                this.showPickingList(order);
                this.fetchPaidOrders(); // Refresh queue
            } else {
                document.getElementById('token-error').style.display = 'block';
            }
        } catch (e) {
            alert('Network error');
        }
    },

    showPickingList: function(order) {
        document.getElementById('picking-modal-customer').textContent = order.customer_name;
        const listDiv = document.getElementById('picking-items-list');
        listDiv.innerHTML = order.items.map(i => `<div>&square; ${i.qty} x ${i.name}</div>`).join('');
        
        document.getElementById('btn-dispatch-complete').onclick = () => {
            this.closeModal('picking-modal');
        };
        
        this.showModal('picking-modal');
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
