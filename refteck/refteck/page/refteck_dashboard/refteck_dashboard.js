/* ─── Pre-register HTML template so it works without bench build ─ */
frappe.templates['refteck_dashboard'] = `<div class="rt-dashboard">

	<!-- Loading overlay -->
	<div class="loading-overlay" id="rtLoadingOverlay" style="display: none;">
		<div class="spinner"></div>
	</div>

	<!-- PAGE HEADER ================================================ -->
	<header>
		<div class="header-left">
			<div class="rt-logo">🌐</div>
			<div>
				<h1>Refteck Group Dashboard</h1>
				<div class="rt-subtitle" id="rtSubtitleDate"></div>
			</div>
		</div>
	</header>

	<!-- ALWAYS-VISIBLE FILTER BAR ================================== -->
	<div class="rt-filter-bar" id="rtFilterBar">

		<!-- Currency toggles -->
		<div class="rt-currency-group" id="rtCurrencyGroup">
			<button class="rt-curr-btn active" data-currency="USD">USD</button>
			<button class="rt-curr-btn" data-currency="EUR">EUR</button>
			<button class="rt-curr-btn" data-currency="GBP">GBP</button>
			<button class="rt-curr-btn" data-currency="INR">INR</button>
		</div>

		<div class="rt-fb-divider"></div>
 
		<!-- Search order — Frappe Link → Sales Order -->
		<div class="rt-link-field-wrap" id="rtSoSearchFieldWrap"></div>
 
		<!-- Party name — Frappe Link → Customer -->
		<div class="rt-link-field-wrap" id="rtPartyFieldWrap"></div>

		<!-- Search order — Frappe Link → Purchase Order -->
		<div class="rt-link-field-wrap" id="rtPoSearchFieldWrap"></div>
 
		<!-- Party name — Frappe Link → Supplier -->
		<div class="rt-link-field-wrap" id="rtSupplierFieldWrap"></div>
		
		<!-- Payment Term -->
		<div class="rt-link-field-wrap" id="rtPaymentTermFieldWrap"></div>

		<!-- Date range -->
		<div class="rt-date-range-wrap">
			<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--rt-text-muted);flex-shrink:0"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
			<input type="date" class="rt-fdate" id="rtFromDate" title="From Date">
			<span class="rt-date-sep">&#8212;</span>
			<input type="date" class="rt-fdate" id="rtToDate" title="To Date">
		</div>

		<!-- Clear -->
		<button class="rt-fbtn rt-fbtn-clear" id="rtClearFiltersBtn" title="Clear all filters">
			<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
			Clear
		</button>

		<!-- Reset / Refresh -->
		<button class="rt-fbtn rt-fbtn-reset" id="rtRefreshBtn" title="Refresh">
			<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l.73-1.19"/>
			</svg>
			Refresh
		</button>
	</div>

	<!-- COMPANY STRIP ============================================== -->
	<div class="rt-company-strip" id="rtCompanyStrip">

		<button class="rt-co-btn active" data-company="Refteck Solutions USA Inc." data-currency="USD">
			<span class="rt-co-icon">🇺🇸</span>
			<span class="rt-co-body">
				<span class="rt-co-name">Refteck Solutions USA Inc.</span>
				<span class="rt-co-sub">$ USD &#8212; United States</span>
			</span>
		</button>
		<button class="rt-co-btn" data-company="Refteck Solutions Europe GmbH" data-currency="EUR">
			<span class="rt-co-icon">🇪🇺</span>
			<span class="rt-co-body">
				<span class="rt-co-name">Refteck Solutions Europe GmbH</span>
				<span class="rt-co-sub">&#8364; EUR &#8212; Germany</span>
			</span>
		</button>
		<button class="rt-co-btn" data-company="Refteck Solutions Limited" data-currency="GBP">
			<span class="rt-co-icon">🇬🇧</span>
			<span class="rt-co-body">
				<span class="rt-co-name">Refteck Solutions Limited</span>
				<span class="rt-co-sub">&#163; GBP &#8212; United Kingdom</span>
			</span>
		</button>
		<button class="rt-co-btn" data-company="Refteck Solution (Pvt.) Limited" data-currency="INR">
			<span class="rt-co-icon">🇮🇳</span>
			<span class="rt-co-body">
				<span class="rt-co-name">Refteck Solution (Pvt.) Limited</span>
				<span class="rt-co-sub">&#8377; INR &#8212; India</span>
			</span>
		</button>
	</div>

	<!-- TAB NAVIGATION ============================================= -->
	<div class="rt-tabs" id="rtTabs">
		<button class="rt-tab active" data-tab="dashboard">&#128202; Dashboard</button>
		<button class="rt-tab" data-tab="purchase-orders">&#128203; Purchase Orders</button>
		<button class="rt-tab" data-tab="sales-orders">&#129534; Sales Orders</button>
		<button class="rt-tab" data-tab="production">&#9881;&#65039; Production</button>
		<button class="rt-tab" data-tab="shipments">&#128674; Shipments</button>
		<button class="rt-tab" data-tab="collections">&#128176; AR Collections</button>
		<button class="rt-tab" data-tab="intercompany">&#128279; Intercompany</button>
	</div>

	<!-- TAB: DASHBOARD ============================================= -->
	<div class="rt-tab-content active" id="tab-dashboard">
		<div class="cards" id="rt_cards_overview"></div>
		<div class="box table-box">
			<div class="bt">Orders Received <span class="badge rt-count" id="cnt_orders">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Party Name</th><th>Amount</th><th>Order Date</th><th>Payment Terms</th><th>Due Date</th><th>Status</th><th>Overdue</th></tr></thead>
				<tbody id="tb_orders"><tr><td colspan="8" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
        


        <div class="box table-box">
            <div class="bt">Ready for Dispatch <span class="badge rt-count" id="cnt_dispatch">0</span></div>
            <div class="table-responsive">
                <table><thead><tr><th>Order No.</th><th>Party</th><th>Value</th><th>Ready Date</th></tr></thead>
                <tbody id="tb_dispatch"><tr><td colspan="4" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
            </div>
        </div>
		<div class="box table-box">
			<div class="bt">Post-Shipment <span class="badge rt-count" id="cnt_post">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Party Name</th><th>Order Value</th><th>Arrived</th><th>Invoice No.</th><th>Payment Status</th><th>Payment Amount</th><th>Payment Date</th></tr></thead>
				<tbody id="tb_post"><tr><td colspan="8" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
	</div>

	<!-- TAB: PURCHASE ORDERS ======================================= -->
	<div class="rt-tab-content" id="tab-purchase-orders">
		<div class="cards" id="rt_cards_po"></div>
		<div class="box table-box">
			<div class="bt">Purchase Orders <span class="badge rt-count" id="cnt_po">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>PO No.</th><th>Company</th><th>Supplier</th><th>PO Value</th><th>Currency</th><th>Payment Type</th></tr></thead>
				<tbody id="tb_po"><tr><td colspan="6" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
	</div>

	<!-- TAB: SALES ORDERS ========================================== -->
	<div class="rt-tab-content" id="tab-sales-orders">
		<div class="cards" id="rt_cards_so"></div>
		<div class="box table-box">
			<div class="bt">Sales Orders <span class="badge rt-count" id="cnt_so">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>SO No.</th><th>Company</th><th>Customer</th><th>SO Value</th><th>Currency</th></tr></thead>
				<tbody id="tb_so"><tr><td colspan="5" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
	</div>

	<!-- TAB: PRODUCTION ============================================ -->
	<div class="rt-tab-content" id="tab-production">
		<div class="box table-box">
			<div class="bt">Purchase Orders Under Production <span class="badge rt-count" id="cnt_prod_tab">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Supplier Name</th><th>Value</th><th>Start Date</th><th>Est. Completion</th></tr></thead>
				<tbody id="tb_prod_tab"><tr><td colspan="5" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
	</div>

	<!-- TAB: SHIPMENTS ============================================= -->
	<div class="rt-tab-content" id="tab-shipments">
		<div class="cards" id="rt_cards_ship"></div>

		<div class="box table-box">
			<div class="bt">Pending ─ Awaiting Freight Forwarder  <span class="badge rt-count" id="cnt_ship_all">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Party Name</th><th>Value</th><th>Packed Date</th></tr></thead>
				<tbody id="tb_ship_all"><tr><td colspan="3" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
		<div class="box table-box">
            <div class="bt">Sea Shipments <span class="badge rt-count" id="cnt_sea">0</span></div>
            <div class="table-responsive">
                <table><thead><tr><th>Invoice No.</th><th>Party Name</th><th>B/L Number</th><th>Value</th><th>ETA</th></tr></thead>
                <tbody id="tb_sea"><tr><td colspan="5" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
            </div>
        </div>
        <div class="box table-box">
            <div class="bt">Air Shipments <span class="badge rt-count" id="cnt_air">0</span></div>
            <div class="table-responsive">
                <table><thead><tr><th>Invoice No.</th><th>Party Name</th><th>AWB Number</th><th>Value</th><th>ETA</th></tr></thead>
                <tbody id="tb_air"><tr><td colspan="5" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
            </div>
        </div>

		
	</div>

	<!-- TAB: AR COLLECTIONS ======================================== -->
	<div class="rt-tab-content" id="tab-collections">
		<div class="cards" id="rt_cards_ar"></div>
		<div class="box table-box">
			<div class="bt">Payment Collection Details <span class="badge rt-count" id="cnt_coll">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Party</th><th>Paid Value</th></tr></thead>
				<tbody id="tb_coll"><tr><td colspan="3" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
		<div class="box table-box" style="margin-top:16px">
			<div class="bt">Pending Collections <span class="badge rt-count" id="cnt_pending_coll">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>Order No.</th><th>Party</th><th>Outstanding</th></thead>
				<tbody id="tb_pending_coll"><tr><td colspan="3" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
	</div>

	<!-- TAB: INTERCOMPANY ========================================== -->
	<div class="rt-tab-content" id="tab-intercompany">
		<div class="cards" id="rt_cards_ic"></div>
		<div class="box table-box">
			<div class="bt">Intercompany Sales Order <span class="badge rt-count" id="cnt_ic">0</span></div>
			<div class="table-responsive">
				<table><thead><tr><th>SO No.</th><th>Company</th><th>Customer</th><th>SO Value</th><th>Currency</th></thead>
				<tbody id="tb_ic"><tr><td colspan="5" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading...</td></tr></tbody></table>
			</div>
		</div>
</div>

	<!-- DASHBOARD FOOTER =========================================== -->
	<footer class="rt-dashboard-footer">
		<a
			href="https://docs.google.com/spreadsheets/d/1NH8Yc-toHJNiTIkxnmJ9d1AV7Cx9Ph_WjhJcVS4zSI0"
			target="_blank"
			rel="noopener noreferrer"
			class="rt-footer-sheet-link"
		>
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
				<polyline points="14 2 14 8 20 8"/>
				<line x1="16" y1="13" x2="8" y2="13"/>
				<line x1="16" y1="17" x2="8" y2="17"/>
				<polyline points="10 9 9 9 8 9"/>
			</svg>
			Dashboard Logic Google Sheet
		</a>

		<span class="rt-footer-powered">
			Powered by
			<a href="https://greycube.in" target="_blank" rel="noopener noreferrer">
				GreyCube Technologies
			</a>
		</span>
	</footer>

</div>
`;
/* ─── Page Entry Points ───────────────────────────────────────── */
frappe.pages['refteck-dashboard'].on_page_load = function (wrapper) {
	const loadScript = (src) => {
		return new Promise((resolve, reject) => {
			// if (src.includes('chart.js') && window.Chart) return resolve();
			if (src.includes('datalabels') && window.ChartDataLabels) return resolve();
			const script = document.createElement('script');
			script.src = src;
			script.onload = resolve;
			script.onerror = reject;
			document.head.appendChild(script);
		});
	};

	loadScript('https://cdn.jsdelivr.net/npm/chart.js@4')
		.then(() => loadScript('https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2'))
		.catch(err => {
			console.error('Failed to load Chart.js:', err);
			frappe.msgprint(__('Failed to load chart libraries. Please refresh.'));
			throw err;
		})
		.then(() => {
			try {
				wrapper.refteck_dashboard = new RefteckDashboard(wrapper);
			} catch (err) {
				console.error('Failed to initialize Refteck Dashboard:', err);
				frappe.msgprint(__('Failed to initialize the dashboard. Please refresh.'));
			}
		});
};

frappe.pages['refteck-dashboard'].on_page_hide = function (wrapper) {
	if (wrapper.refteck_dashboard) {
		wrapper.refteck_dashboard.cleanup();
	}
};

/* ─── Dashboard Class ─────────────────────────────────────────── */
class RefteckDashboard {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __('Refteck Dashboard'),
			single_column: true
		});

		$(this.page.page_title).hide();
		$(wrapper).find('.page-head').hide();

		this.applyFullWidth();

		this.data = {};
		this.filterFields = {};
		this.activeTab = 'dashboard';
		this.lastLoadedFilters = {};

		// FX rates (defaults, loaded from API)
		this.fx = { USD: 1, EUR: 0.92, GBP: 0.79, INR: 0.012 };
		this.symMap = { USD: '$', EUR: '€', GBP: '£', INR: '₹' };

		this.init();
	}

	applyFullWidth() {
		this.modifiedElements = [];
		const fullWidthStyle = { maxWidth: '100%', width: '100%', paddingLeft: '0', paddingRight: '0', marginLeft: '0', marginRight: '0' };
		const applyStyle = (el) => {
			if (!el || !el.style) return;
			if (this.modifiedElements.some(item => item.el === el)) return;
			if (el.classList && (el.classList.contains('navbar') || el.closest('.navbar'))) return;
			const original = { el, maxWidth: el.style.maxWidth, width: el.style.width, paddingLeft: el.style.paddingLeft, paddingRight: el.style.paddingRight, marginLeft: el.style.marginLeft, marginRight: el.style.marginRight };
			this.modifiedElements.push(original);
			Object.assign(el.style, fullWidthStyle);
		};
		const dashboardEl = this.page.body.find('.rt-dashboard');
		if (dashboardEl.length) {
			let el = dashboardEl[0].parentElement;
			while (el && el.tagName !== 'BODY') {
				if (el.classList && !el.classList.contains('navbar') && !el.closest('.navbar')) {
					if (el.classList.contains('page-container')) break;
					const containerClasses = ['layout-main-section', 'layout-main-section-wrapper', 'page-content', 'container', 'col-lg-12', 'col-md-12', 'frappe-control'];
					if (containerClasses.some(c => el.classList.contains(c))) applyStyle(el);
				}
				el = el.parentElement;
			}
		}
	}

	cleanup() {
		if (this.modifiedElements) {
			this.modifiedElements.forEach(item => {
				if (item.el && item.el.style) {
					item.el.style.maxWidth = item.maxWidth || '';
					item.el.style.width = item.width || '';
					item.el.style.paddingLeft = item.paddingLeft || '';
					item.el.style.paddingRight = item.paddingRight || '';
					item.el.style.marginLeft = item.marginLeft || '';
					item.el.style.marginRight = item.marginRight || '';
				}
			});
			this.modifiedElements = [];
		}
	}

	init() {
		$(frappe.render_template('refteck_dashboard', {})).appendTo(this.page.body);

		this.initElements();
		this.initFrappeFilters();   // creates the Link controls — must run first
		this.bindEvents();
		const restoredTab = this.restoreFromUrl();

		if (restoredTab) {
			this.switchTab(restoredTab);   // lands directly on the saved tab with saved filters
		} else {
			this.refresh();                // first-ever visit, no URL state yet
		}

	}

	initElements() {
		this.refreshBtn = document.getElementById('rtRefreshBtn');
		this.loadingOverlay = document.getElementById('rtLoadingOverlay');
		this.clearFiltersBtn = document.getElementById('rtClearFiltersBtn');
	}

	initFrappeFilters() {
		// Filters are now always-visible native HTML inputs in rt-filter-bar.
		// Set default date range (last month) on the native date inputs.
		const { fromDate, toDate } = this.getQuickPeriodDates('last_month');
		const fromEl = document.getElementById('rtFromDate');
		const toEl = document.getElementById('rtToDate');
		if (fromEl) fromEl.value = fromDate;
		if (toEl) toEl.value = toDate;

		// Update subtitle with today date
		const subEl = document.getElementById('rtSubtitleDate');
		if (subEl) {
			subEl.textContent = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
		}

		this.filterFields.so_search = frappe.ui.form.make_control({
			df: {
				fieldtype: 'Link',
				fieldname: 'so_search',
				label: __('Sales Order'),
				options: 'Sales Order',
				placeholder: __('Search Sales Order...'),
				// Example for so_search — apply the same one-line guard to party_name, po_search, supplier, payment_term
				change: () => {
					if (this._restoringFromUrl) return;
					clearTimeout(this._soTimer);
					this._soTimer = setTimeout(() => this.refresh(), 400);
				}
			},
			parent: document.getElementById('rtSoSearchFieldWrap'),
			render_input: true,
		});

		// ── Frappe Link field: Customer ─────────────────────────────
		this.filterFields.party_name = frappe.ui.form.make_control({
			df: {
				fieldtype: 'Link',
				fieldname: 'party_name',
				label: __('Customer'),
				options: 'Customer',
				placeholder: __('Party name...'),
				change: () => {
					if (this._restoringFromUrl) return;
					clearTimeout(this._partyTimer);
					this._partyTimer = setTimeout(() => this.refresh(), 400);
				}
			},
			parent: document.getElementById('rtPartyFieldWrap'),
			render_input: true
		});

		this.filterFields.po_search = frappe.ui.form.make_control({
			df: {
				fieldtype: 'Link',
				fieldname: 'po_search',
				label: __('Purchase Order'),
				options: 'Purchase Order',
				placeholder: __('Search Purchase Order...'),
				change: () => {
					if (this._restoringFromUrl) return;
					clearTimeout(this._poTimer);                
					this._poTimer = setTimeout(() => this.refresh(), 400);
				}
			},
			parent: document.getElementById('rtPoSearchFieldWrap'),
			render_input: true
		});

		this.filterFields.supplier = frappe.ui.form.make_control({
			df: {
				fieldtype: 'Link',
				fieldname: 'supplier',
				label: __('Supplier'),
				options: 'Supplier',
				placeholder: __('Supplier...'),
				change: () => {
					if (this._restoringFromUrl) return;
					clearTimeout(this._supplierTimer);          
					this._supplierTimer = setTimeout(() => this.refresh(), 400);
				}
			},
			parent: document.getElementById('rtSupplierFieldWrap'),
			render_input: true
		});

		this.filterFields.payment_term = frappe.ui.form.make_control({
			df: {
				fieldtype: 'Link',
				fieldname: 'payment_term',
				label: __('Payment Term'),
				options: 'Payment Terms Template',
				placeholder: __('Payment Term...'),
				change: () => {
					if (this._restoringFromUrl) return;
					clearTimeout(this._paymentTermTimer); 
					this._paymentTermTimer = setTimeout(() => this.refresh(), 400);
				}
			},
			parent: document.getElementById('rtPaymentTermFieldWrap'),
			render_input: true
		});

	}

	bindEvents() {
		// Refresh/Reset button
		if (this.refreshBtn) this.refreshBtn.addEventListener('click', () => this.refresh(true));
		// Clear button
		const clearBtn = document.getElementById('rtClearFiltersBtn');
		if (clearBtn) clearBtn.addEventListener('click', () => this.clearFilters());

		// Live filter: any change in the filter bar triggers a refresh after short debounce
		const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
		const debouncedRefresh = debounce(() => this.refresh(), 600);

		['rtFromDate', 'rtToDate'].forEach(id => {
			const el = document.getElementById(id);
			if (el) el.addEventListener('change', () => this.refresh());
		});

		// Currency group
		const currGroup = document.getElementById('rtCurrencyGroup');
		if (currGroup) {
			currGroup.addEventListener('click', (e) => {
				const btn = e.target.closest('.rt-curr-btn');
				if (!btn) return;
				currGroup.querySelectorAll('.rt-curr-btn').forEach(b => b.classList.remove('active'));
				btn.classList.add('active');
				this.refresh();
			});
		}

		// Tab switching
		document.getElementById('rtTabs').addEventListener('click', (e) => {
			const btn = e.target.closest('.rt-tab');
			if (btn) this.switchTab(btn.dataset.tab);
		});

		// Company strip
		document.getElementById('rtCompanyStrip').addEventListener('click', (e) => {
			const btn = e.target.closest('.rt-co-btn');
			if (!btn) return;
			this.syncCompanyAndCurrency(btn.dataset.currency);
			// document.querySelectorAll('.rt-co-btn').forEach(b => b.classList.remove('active'));
			// btn.classList.add('active');
			// document.querySelectorAll('.rt-curr-btn').forEach(b =>
			// 	b.classList.toggle('active', b.dataset.currency === btn.dataset.currency));
			// this.refresh();
		});

		document.getElementById('rtCurrencyGroup').addEventListener('click', (e) => {
			const btn = e.target.closest('.rt-curr-btn');
			if (!btn) return;
			this.syncCompanyAndCurrency(btn.dataset.currency);
		});
	}

	// Single source of truth — finds the company button matching a currency, activates both
	syncCompanyAndCurrency(currency) {
		// Find the matching company button by its EXISTING data-currency attribute
		// querySelectorAll preserves DOM order, so [0] = first match in markup order
		const matches = document.querySelectorAll(`.rt-co-btn[data-currency="${currency}"]`);
		const companyBtn = matches[0];   // for USD this picks whichever button appears first (All Companies, since it's listed first)

		if (!companyBtn) return;

		document.querySelectorAll('.rt-co-btn').forEach(b =>
			b.classList.toggle('active', b === companyBtn));

		document.querySelectorAll('.rt-curr-btn').forEach(b =>
			b.classList.toggle('active', b.dataset.currency === currency));

		this.refresh();
	}

	getFiltersFingerprint(filters) {
		// Cheap deterministic string to compare "did filters actually change"
		return JSON.stringify(filters);
	}


	switchTab(name) {
		document.querySelectorAll('.rt-tab-content').forEach(p => p.classList.remove('active'));
		document.querySelectorAll('.rt-tab').forEach(b => b.classList.remove('active'));
		const panel = document.getElementById('tab-' + name);
		if (panel) panel.classList.add('active');
		document.querySelectorAll('.rt-tab').forEach(b => { if (b.dataset.tab === name) b.classList.add('active'); });
		this.activeTab = name;

		const fp = this.getFiltersFingerprint(this.getFilters());
		if (this.lastLoadedFilters[name] !== fp) {
			this.lastLoadedFilters[name] = fp;
			this.renderTab(name);
		}

		this.syncUrl();
	}

	renderTab(name) {
		const filters = this.getFilters();
		switch (name) {
			case 'dashboard': this.renderDashboardTab(filters); break;
			case 'purchase-orders': this.renderPurchaseOrdersTab(filters); break;
			case 'sales-orders': this.renderSalesOrdersTab(filters); break;
			case 'production': this.renderProductionTab(filters); break;
			case 'shipments': this.renderShipmentsTab(filters); break;
			case 'collections': this.renderCollectionsTab(filters); break;
			case 'intercompany': this.renderIntercompanyTab(filters); break;
		}
	}

	getFilters() {
		// Read directly from always-visible inline filter bar (native HTML inputs)
		const fromEl = document.getElementById('rtFromDate');
		const toEl = document.getElementById('rtToDate');
		const activeCurr = document.querySelector('.rt-curr-btn.active');
		const activeCo = document.querySelector('.rt-co-btn.active');
		return {
			from_date: fromEl?.value || frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			to_date: toEl?.value || frappe.datetime.get_today(),
			company: activeCo?.dataset?.company || '',
			// currency:      activeCurr?.dataset?.currency || 'USD',
			so: this.filterFields.so_search?.get_value() || '',
			party: this.filterFields.party_name?.get_value() || '',
			po: this.filterFields.po_search?.get_value() || '',
			supplier: this.filterFields.supplier?.get_value() || '',
			payment_term: this.filterFields.payment_term?.get_value() || '',
		};
	}

	/* ─── FX & formatting ──────────────────────────────────────── */
	fmtNative(val, cur) {
		const sym = this.symMap[cur] || '';
		const abs = Math.abs(val || 0);
		// if (abs >= 1e6) return sym + (val / 1e6).toFixed(2) + 'M';
		// if (abs >= 1e3) return sym + (val / 1e3).toFixed(1) + 'K';
		// return sym + Math.round(val || 0).toLocaleString();
		return sym + " " + val
	}

	card(icon, title, value, sub = '', badge = '') {
		const icon_html = icon ? `<div style="font-size: 18px;">${icon}</div>` : `<div></div>`;
		const badge_html = badge ? `<span class="badge">${badge}</span>` : '';

		return `
			<div class="card">
				${icon_html}
				<div class="t">${title}${badge_html}</div>
				<div class="v">${value}</div>
			</div>
			`;
		// return `<div class="card"><div style="font-size: 18px;">${icon}</div> <div class="t">${title}${badge ? `<span class="badge">${badge}</span>` : ''}</div><div class="v">${value}</div>${sub ? `<div class="s">${sub}</div>` : ''}</div>`;
	}

	statusBadge(status) {
		if (!status) return '<span class="rt-badge">—</span>';
		const map = { 'Delivered': 'rt-badge-green', 'Completed': 'rt-badge-green', 'Paid': 'rt-badge-green', 'Cleared': 'rt-badge-green', 'Confirmed': 'rt-badge-blue', 'In Progress': 'rt-badge-blue', 'In Transit': 'rt-badge-blue', 'Shipped': 'rt-badge-blue', 'Pending': 'rt-badge-amber', 'Ready for Dispatch': 'rt-badge-green', 'Awaiting Freight Forwarder': 'rt-badge-amber', 'In Production': 'rt-badge-purple', 'Overdue': 'rt-badge-red', 'Urgent': 'rt-badge-red', 'Cancelled': 'rt-badge-red', 'Partial': 'rt-badge-blue', 'Current': 'rt-badge-green' };
		return `<span class="rt-badge ${map[status] || ''}">${status}</span>`;
	}

	fmtDate(d) { if (!d) return '—'; try { return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }); } catch { return d; } }

	loadingRow(cols) { return `<tr><td colspan="${cols}" class="rt-loading-row"><div class="rt-spinner-sm"></div> Loading from ERPNext…</td></tr>`; }
	slowLoadingRow(cols) {
		return `<tr><td colspan="${cols}" class="rt-loading-row">
        <div class="rt-spinner-sm"></div> Still fetching — this report has a lot of data…
    </td></tr>`;
	}
	emptyRow(msg, cols) { return `<tr><td colspan="${cols}" class="rt-empty-row">📭 ${msg}</td></tr>`; }

	/* ─── Refresh ──────────────────────────────────────────────── */

	async refresh(clearCache = false) {
		// console.log("---refteshh---")
		delete this.lastLoadedFilters[this.activeTab];   // force-reload only the visible tab
		try {
			await this.renderTab(this.activeTab);
			this.lastLoadedFilters[this.activeTab] = this.getFiltersFingerprint(this.getFilters());
			this.syncUrl();

			if (clearCache) frappe.show_alert({ message: __('Refreshed'), indicator: 'green' }, 3);
		} catch (e) {
			console.error(e);
			frappe.msgprint({ title: __('Error'), message: __('Failed to load data.'), indicator: 'red' });
		}
	}

	syncUrl() {
		const f = this.getFilters();
		const params = new URLSearchParams();
		params.set('tab', this.activeTab);
		if (f.from_date) params.set('from_date', f.from_date);
		if (f.to_date) params.set('to_date', f.to_date);
		if (f.company) params.set('company', f.company);
		if (f.currency) params.set('currency', f.currency);
		if (f.so) params.set('so', f.so);
		if (f.party) params.set('party', f.party);
		if (f.po) params.set('po', f.po);
		if (f.supplier) params.set('supplier', f.supplier);
		if (f.payment_term) params.set('payment_term', f.payment_term);

		const newUrl = `${window.location.pathname}?${params.toString()}`;
		window.history.replaceState(null, '', newUrl);
	}

	restoreFromUrl() {
		const params = new URLSearchParams(window.location.search);
		if (![...params.keys()].length) return false;   // nothing to restore

		this._restoringFromUrl = true;   // suppress the change-callback refresh storm below

		const fromEl = document.getElementById('rtFromDate');
		const toEl = document.getElementById('rtToDate');
		if (params.get('from_date') && fromEl) fromEl.value = params.get('from_date');
		if (params.get('to_date') && toEl) toEl.value = params.get('to_date');

		if (params.get('currency')) {
			document.querySelectorAll('.rt-curr-btn').forEach(b =>
				b.classList.toggle('active', b.dataset.currency === params.get('currency')));
		}
		if (params.get('company')) {
			document.querySelectorAll('.rt-co-btn').forEach(b =>
				b.classList.toggle('active', b.dataset.company === params.get('company')));
		}

		// Link fields exist only after initFrappeFilters() has run — see init() change below
		if (params.get('so')) this.filterFields.so_search?.set_value(params.get('so'));
		if (params.get('party')) this.filterFields.party_name?.set_value(params.get('party'));
		if (params.get('po')) this.filterFields.po_search?.set_value(params.get('po'));
		if (params.get('supplier')) this.filterFields.supplier?.set_value(params.get('supplier'));
		if (params.get('payment_term')) this.filterFields.payment_term?.set_value(params.get('payment_term'));

		this._restoringFromUrl = false;
		return params.get('tab') || null;
	}

	/* ─── TAB: DASHBOARD ───────────────────────────────────────── */

	async renderDashboardTab(filters) {
		const f = filters || this.getFilters();
		this.loadOverviewCards(f);
		this.loadTable('tb_orders', f, 'get_orders_received', this.renderOrdersRows.bind(this), 'cnt_orders', 8);
		this.loadTable('tb_dispatch', f, 'get_ready_for_dispatch', this.renderDispatchRows.bind(this), 'cnt_dispatch', 4);
		this.loadTable('tb_post', f, 'get_post_shipment', this.renderPostRows.bind(this), 'cnt_post', 8);
	}

	async loadOverviewCards(f) {
		try {

			const [r, ar] = await Promise.all([
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_dashboard_metrics', args: { company: f.company, from_date: f.from_date, to_date: f.to_date, so: f.so, party: f.party, payment_term: f.payment_term, po: f.po, supplier: f.supplier } }),
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_ar_collection_kpis', args: { company: f.company, to_date: f.to_date } })
			]);

			const d = r.message || {};
			const ad = ar.message || {};

			document.getElementById('rt_cards_overview').innerHTML = [
				this.card('📦', 'Total Orders', this.fmtNative(d.total_orders, d.currency) ?? '—'),
				this.card('🚢', 'Sea Shipments', this.fmtNative(d.sea_shipments, d.currency) ?? '—'),
				this.card('✈️', 'Air Shipments', this.fmtNative(d.air_shipments, d.currency) ?? '—'),
				this.card('⏳', 'Active Orders', (d.active_orders || 0) ?? '—'),
				this.card('🚛', 'Open Shipment', this.fmtNative(d.open_shipment, d.currency) ?? '—'),
				this.card('💰', 'Collected', this.fmtNative(ad.total_paid_collection || 0, d.currency) ?? '—'),
				this.card('📈', 'Gross Margin', this.fmtNative(d.total_gross_margin, d.currency) ?? '—'),
				this.card('📊', 'Shipment Ratio', this.fmtNative(d.shipment_ratio, d.currency) ?? '—'),
				this.card('✅', 'Overdue Orders', (d.overdue_so || 0) ?? '—'),
				this.card('🧾', 'Account Receivable', this.fmtNative(ad.total_acc_receivable, d.currency) ?? '—'),
				this.card('💳', 'AP Advance Paid', this.fmtNative(d.ap_advance_paid, d.currency) ?? '—'),
				this.card('🔗', 'IC Exposure', (d.ic_exposure || 0) ?? '—'),
			].join('');
		} catch (e) { console.error(e); }
	}

	/* ─── Generic table loader ──────────────────────────────────── */
	async loadTable(tbodyId, f, method, renderFn, cntId, cols) {
		const tbody = document.getElementById(tbodyId); if (!tbody) return;
		tbody.innerHTML = this.loadingRow(cols);
		try {
			const r = await frappe.call({ method: `refteck.refteck.page.refteck_dashboard.refteck_dashboard.${method}`, args: { company: f.company, so: f.so, from_date: f.from_date, to_date: f.to_date, party: f.party, payment_term: f.payment_term, po: f.po, supplier: f.supplier } });
			const rows = r.message || [];
			if (cntId) { const el = document.getElementById(cntId); if (el) el.textContent = rows.length; }
			tbody.innerHTML = rows.length ? rows.map(renderFn).join('') : this.emptyRow('No records found', cols);
		} catch (e) { tbody.innerHTML = this.emptyRow('Error loading data', cols); }
	}

	/* ─── Row renderers ─────────────────────────────────────────── */
	renderOrdersRows(o) { return `<tr><td><a href="/app/sales-order/${o.order_no}" style="color:var(--rt-teal)">${o.order_no}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${this.fmtNative(o.amount, o.currency)}</td><td>${this.fmtDate(o.order_date)}</td><td>${o.payment_terms || '—'}</td><td>${this.fmtDate(o.due_date)}</td><td>${this.statusBadge(o.status)}</td><td>${o.overdue_days > 0 ? `<span class="rt-badge rt-badge-red">${o.overdue_days}</span>` : `<span class="rt-badge rt-badge-green"> ${o.overdue_days}</span>`}</td></tr>`; }

	renderSeaRows(o) { return `<tr><td><a href="/app/sales-invoice/${o.invoice_no}" style="color:var(--rt-blue)">${o.invoice_no}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${o.airway_bill || '—'}</td><td class="rt-mono">${this.fmtNative(o.amount, o.currency)}</td><td>${this.fmtDate(o.delivery_date)}</td></tr>`; }

	renderAirRows(o) { return `<tr><td><a href="/app/sales-invoice/${o.invoice_no}" style="color:var(--rt-blue)">${o.invoice_no}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${o.airway_bill || '—'}</td><td class="rt-mono">${this.fmtNative(o.amount, o.currency)}</td><td>${this.fmtDate(o.delivery_date)}</td></tr>`; }

	renderDispatchRows(o) { return `<tr><td><a href="/app/purchase-order/${o.order_no}" style="color:var(--rt-green)">${o.order_no}</a></td><td>${o.supplier || '—'}</td><td class="rt-mono">${this.fmtNative(o.value, o.currency)}</td><td>${this.fmtDate(o.ready_date)}</td></tr>`; }

	renderPostRows(o) { return `<tr><td><a href="/app/sales-order/${o.order_no}" style="color:var(--rt-teal)">${o.order_no || '—'}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${this.fmtNative(o.amount, o.currency)}</td><td>${this.fmtDate(o.delivery_date)}</td><td><a href="/app/sales-invoice/${o.invoice_no}" style="color:var(--rt-blue)">${o.invoice_no}</a></td><td>${this.statusBadge(o.payment_terms || '—')}</td><td>${o.payment_amount ? this.fmtNative(o.payment_amount, o.currency) : '—'}</td><td>${this.fmtDate(o.payment_date)}</td></tr>`; }

	renderAwaintingFFRows(o) {
		return `<tr><td><a href="/app/sales-invoice/${o.invoice_no}" style="color:var(--rt-amber)">${o.customer_po_no}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${this.fmtNative(o.amount, o.currency)}</td><td>${this.fmtDate(o.packed_date)}</td></tr>`;
	}


	/* ─── TAB: PURCHASE ORDERS ─────────────────────────────────── */
	async renderPurchaseOrdersTab(f) {
		const filters = f || this.getFilters();
		try {
			const [kpiR, tableR] = await Promise.all([
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_purchase_order_kpis', args: { company: filters.company, from_date: f.from_date, to_date: f.to_date } }),
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_purchase_orders', args: { company: filters.company, from_date: f.from_date, to_date: f.to_date, po: f.po, supplier: f.supplier, so: f.so } })
			]);
			const k = kpiR.message || {};
			document.getElementById('rt_cards_po').innerHTML = [
				this.card('', 'Total PO', k.total_pos ?? '—', ''),
				this.card('', 'Advance Req.', k.advance_count ?? '—', ''),
				this.card('', 'Credit Terms', k.credit_count ?? '—', ''),
				this.card('', 'Total PO Value', this.fmtNative(k.total_value, k.currency) ?? '—', ''),
			].join('');
			const rows = tableR.message || [];
			const cnt = document.getElementById('cnt_po'); if (cnt) cnt.textContent = rows.length;
			const tbody = document.getElementById('tb_po');
			tbody.innerHTML = rows.length ? rows.map(o => `
				<tr>
					<td><a href="/app/purchase-order/${o.po_name}" style="color:var(--rt-blue)">${o.customer_po}</a></td>
					<td>${o.company || '—'}</td>
					<td>${o.supplier || '—'}</td>
					<td class="rt-mono">${this.fmtNative(o.po_value, o.currency)}</td>
					<td>${o.currency || '—'}</td>
					<td>${this.statusBadge(o.payment_terms)}</td>
				</tr>`).join('') : this.emptyRow('No purchase orders', 6);
		} catch (e) { console.error(e); }
	}

	/* ─── TAB: SALES ORDERS ────────────────────────────────────── */
	async renderSalesOrdersTab(f) {
		const filters = f || this.getFilters();
		try {
			const [kpiR, tableR] = await Promise.all([
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_sales_order_kpis', args: { company: filters.company, from_date: f.from_date, to_date: f.to_date } }),
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_sales_orders', args: { company: filters.company, so: f.so, from_date: f.from_date, to_date: f.to_date, party: f.party, po: f.po } })
			]);
			const k = kpiR.message || {};
			document.getElementById('rt_cards_so').innerHTML = [
				this.card('', 'Total SO', k.total_so ?? '—', ''),
				this.card('', 'Intercompany', k.ic_count ?? '—', ''),
				this.card('', 'Total SO Value', this.fmtNative(k.total_value || 0, k.currency), ''),
				this.card('', 'Total Advance SO', k.total_so_advance ?? '—', ''),
				this.card('', 'Total Advance SO Value', k.total_so_advance_value ?? '—', ''),
			].join('');
			const rows = tableR.message || [];
			const cnt = document.getElementById('cnt_so'); if (cnt) cnt.textContent = rows.length;
			const tbody = document.getElementById('tb_so');
			tbody.innerHTML = rows.length ? rows.map(o => `
				<tr>
					<td><a href="/app/sales-order/${o.so_name}" style="color:var(--rt-teal)">${o.so_number}</a></td>
					<td>${o.company || '—'}</td>
					<td>${o.customer || '—'}</td>
					<td class="rt-mono">${this.fmtNative(o.so_value, o.currency)}</td>
					<td>${o.currency || '—'}</td>
				</tr>`).join('') : this.emptyRow('No sales orders', 5);
		} catch (e) { console.error(e); }
	}

	/* ─── TAB: PRODUCTION ──────────────────────────────────────── */
	async renderProductionTab(f) {
		const filters = f || this.getFilters();
		const tbody = document.getElementById('tb_prod_tab'); if (!tbody) return;
		tbody.innerHTML = this.loadingRow(5);
		try {
			const r = await frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_production_orders', args: { company: filters.company, from_date: f.from_date, to_date: f.to_date, po: f.po, supplier: f.supplier, so: f.so } });
			const rows = r.message || [];
			const cnt = document.getElementById('cnt_prod_tab'); if (cnt) cnt.textContent = rows.length;
			tbody.innerHTML = rows.length ? rows.map(o => `
				<tr>
					<td><a href="/app/purchase-order/${o.po_name}" style="color:var(--rt-purple)">${o.customer_po}</a></td>
					<td>${o.supplier || '—'}</td>
					<td class="rt-mono">${this.fmtNative(o.value, o.currency)}</td>
					<td>${this.fmtDate(o.start_date)}</td>
					<td>${this.fmtDate(o.est_completion)}</td>
				</tr>`).join('') : this.emptyRow('No production orders', 5);
		} catch (e) { tbody.innerHTML = this.emptyRow('Error loading data', 5); }
	}

	/* ─── TAB: SHIPMENTS ───────────────────────────────────────── */
	async renderShipmentsTab(f) {
		const filters = f || this.getFilters();
			this.loadTable('tb_ship_all', filters, 'get_awaiting_ff', this.renderAwaintingFFRows.bind(this), 'cnt_ship_all', 3);
			this.loadTable('tb_sea', filters, 'get_sea_shipments', this.renderSeaRows.bind(this), 'cnt_sea', 5);
			this.loadTable('tb_air', filters, 'get_air_shipments', this.renderAirRows.bind(this), 'cnt_air', 5);
	}

	/* ─── TAB: AR COLLECTIONS ──────────────────────────────────── */

	async renderCollectionsTab(f) {
		const filters = f || this.getFilters();
		await Promise.all([
			this.loadARCards(filters),
			this.loadTable('tb_coll', filters, 'get_ar_collection_details', (o) => `<tr><td><a href="/app/sales-invoice/${o.order_no}" style="color:var(--rt-teal)">${o.order_no || '—'}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${this.fmtNative(o.value, o.currency)}</td></tr>`, 'cnt_coll', 3),
			this.loadTable('tb_pending_coll', filters, 'get_pending_collections', (o) => `<tr><td><a href="/app/sales-invoice/${o.order_no}" style="color:var(--rt-teal)">${o.order_no || '—'}</a></td><td>${o.party_name || '—'}</td><td class="rt-mono">${this.fmtNative(o.value, o.currency)}</td></tr>`, 'cnt_pending_coll', 3),
		]);
	}

	async loadARCards(f) {
		try {
			const r = await frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_ar_collection_kpis', args: { company: f.company, from_date: f.from_date, to_date: f.to_date } });
			const d = r.message || {};
			document.getElementById('rt_cards_ar').innerHTML = [
				this.card('', 'Pending Collection', this.fmtNative(d.total_pending_collection || 0, d.currency),),
				this.card('', 'Total Invoiced', this.fmtNative(d.total_invoiced || 0, d.currency),),
			].join('');
		} catch (e) { console.error(e); }
	}


	/* ─── TAB: INTERCOMPANY ────────────────────────────────────── */

	async renderIntercompanyTab(f) {
		const filters = f || this.getFilters();
		try {
			const [tableR] = await Promise.all([
				frappe.call({ method: 'refteck.refteck.page.refteck_dashboard.refteck_dashboard.get_intercompany_transactions', args: { company: filters.company, so: filters.so, from_date: filters.from_date, to_date: filters.to_date, party: filters.party, po: f.po } }),
			]);

			const rows = tableR.message || [];
			const cnt = document.getElementById('cnt_ic'); if (cnt) cnt.textContent = rows.length;
			document.getElementById('tb_ic').innerHTML = rows.length ? rows.map(o => `
				<tr>
					<td><a href="/app/sales-order/${o.so_name}" style="color:var(--rt-teal)">${o.so_number}</a></td>
					<td>${o.company || '—'}</td>
					<td>${o.customer || '—'}</td>
					<td class="rt-mono">${this.fmtNative(o.so_value, o.currency)}</td>
					<td>${o.currency || '—'}</td>
				</tr>`).join('') : this.emptyRow('No Inter Company transactions', 5);
		} catch (e) { console.error(e); }
	}

	/* ─── Filter popup helpers ──────────────────────────────────── */
	clearFilters() {
		const { fromDate, toDate } = this.getQuickPeriodDates('last_month');
		const fromEl = document.getElementById('rtFromDate');
		const toEl = document.getElementById('rtToDate');
		if (fromEl) fromEl.value = fromDate;
		if (toEl) toEl.value = toDate;
		this.filterFields.so_search?.set_value('');
		this.filterFields.party_name?.set_value('');
		this.filterFields.po_search?.set_value('');
		this.filterFields.supplier?.set_value('');
		this.filterFields.payment_term?.set_value('');

		// Reset currency to USD
		document.querySelectorAll('.rt-curr-btn').forEach(b => b.classList.toggle('active', b.dataset.currency === 'USD'));
		// Reset company to All
		// document.querySelectorAll('.rt-co-btn').forEach(b => b.classList.toggle('active', b.dataset.company === 'Refteck Solutions USA Inc.'));
		document.querySelector('.rt-co-btn')?.classList.add('active');
		this.refresh();
	}

	getQuickPeriodDates(period) {
		const now = new Date(); const y = now.getFullYear(); const m = now.getMonth(); const d = now.getDate();
		const fmtNative = (dt) => { const yr = dt.getFullYear(); const mo = String(dt.getMonth() + 1).padStart(2, '0'); const dy = String(dt.getDate()).padStart(2, '0'); return `${yr}-${mo}-${dy}`; };
		const today = fmtNative(now);
		const lastDay = (yr, mo) => new Date(yr, mo + 1, 0).getDate();
		let from, to;
		switch (period) {
			case 'today': from = to = today; break;
			case 'yesterday': { const yd = new Date(y, m, d - 1); from = to = fmtNative(yd); break; }
			case 'this_week': { const ws = new Date(y, m, d - now.getDay()); from = fmtNative(ws); to = today; break; }
			case 'last_week': { const lwe = new Date(y, m, d - now.getDay() - 1); const lws = new Date(y, m, d - now.getDay() - 7); from = fmtNative(lws); to = fmtNative(lwe); break; }
			case 'this_month': from = `${y}-${String(m + 1).padStart(2, '0')}-01`; to = today; break;
			case 'last_month': { const ly = m === 0 ? y - 1 : y; const lm = m === 0 ? 11 : m - 1; from = `${ly}-${String(lm + 1).padStart(2, '0')}-01`; to = `${ly}-${String(lm + 1).padStart(2, '0')}-${String(lastDay(ly, lm)).padStart(2, '0')}`; break; }
			case 'last_30_days': { const ago = new Date(y, m, d - 30); from = fmtNative(ago); to = today; break; }
			case 'this_quarter': { const qs = Math.floor(m / 3) * 3; from = `${y}-${String(qs + 1).padStart(2, '0')}-01`; to = today; break; }
			case 'last_quarter': { const cq = Math.floor(m / 3); const lqy = cq === 0 ? y - 1 : y; const lqs = cq === 0 ? 9 : (cq - 1) * 3; const lqe = lqs + 2; from = `${lqy}-${String(lqs + 1).padStart(2, '0')}-01`; to = `${lqy}-${String(lqe + 1).padStart(2, '0')}-${String(lastDay(lqy, lqe)).padStart(2, '0')}`; break; }
			case 'this_year': from = `${y}-01-01`; to = today; break;
			case 'last_year': from = `${y - 1}-01-01`; to = `${y - 1}-12-31`; break;
			default: { const ago = new Date(y, m, d - 30); from = fmtNative(ago); to = today; }
		}
		return { fromDate: from, toDate: to };
	}
}