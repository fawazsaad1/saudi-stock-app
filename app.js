// Global Variables
let currentStocks = [];
let currentChart = null;
let indicatorsChart = null;

// API Base URL
const API_BASE = '/api';

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadMarketSummary();
    loadTopStocks();
    loadSectorsChart();
    loadPopularIndicators();
});

// Initialize Application
function initializeApp() {
    // Initialize stocks data
    initializeStocks();
    
    // Load stock options for indicators
    loadStockOptions();
    
    showToast('مرحباً بك في تطبيق السوق السعودي', 'success');
}

// Setup Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            showSection(section);
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Stock search
    const searchInput = document.getElementById('stock-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterStocks(this.value);
        });
    }
    
    // Modal close
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('stock-modal');
        if (e.target === modal) {
            closeStockModal();
        }
    });
}

// Show Section
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Load Market Summary
async function loadMarketSummary() {
    try {
        const response = await fetch(`${API_BASE}/market/summary`);
        const data = await response.json();
        
        if (data.success) {
            updateMarketSummary(data.data);
        }
    } catch (error) {
        console.error('Error loading market summary:', error);
        // Use mock data
        updateMarketSummary({
            tasi_index: { value: 11276.91, change: -32.45, change_percent: -0.29 },
            volume: 156789000,
            trades: 45678
        });
    }
}

// Update Market Summary
function updateMarketSummary(data) {
    const tasiValue = document.getElementById('tasi-value');
    const tasiChange = document.getElementById('tasi-change');
    const volumeValue = document.getElementById('volume-value');
    const tradesValue = document.getElementById('trades-value');
    
    if (tasiValue && data.tasi_index) {
        tasiValue.textContent = data.tasi_index.value.toLocaleString('ar-SA');
        
        if (tasiChange) {
            const changeText = `${data.tasi_index.change} (${data.tasi_index.change_percent}%)`;
            tasiChange.textContent = changeText;
            tasiChange.className = `change ${data.tasi_index.change >= 0 ? 'positive' : 'negative'}`;
        }
    }
    
    if (volumeValue && data.volume) {
        volumeValue.textContent = (data.volume / 1000000).toFixed(1) + ' مليون';
    }
    
    if (tradesValue && data.trades) {
        tradesValue.textContent = data.trades.toLocaleString('ar-SA');
    }
}

// Initialize Stocks
async function initializeStocks() {
    showLoading();
    
    try {
        // Initialize stocks in database
        const initResponse = await fetch(`${API_BASE}/stocks/init`, {
            method: 'POST'
        });
        
        // Load stocks
        const response = await fetch(`${API_BASE}/stocks`);
        const data = await response.json();
        
        if (data.success) {
            currentStocks = data.data;
            displayStocks(currentStocks);
            showToast('تم تحديث بيانات الأسهم بنجاح', 'success');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error initializing stocks:', error);
        // Use mock data
        currentStocks = generateMockStocks();
        displayStocks(currentStocks);
        showToast('تم استخدام بيانات تجريبية', 'info');
    } finally {
        hideLoading();
    }
}

// Generate Mock Stocks
function generateMockStocks() {
    const mockStocks = [
        { symbol: '2222', name: 'أرامكو السعودية', sector: 'الطاقة' },
        { symbol: '1120', name: 'الراجحي', sector: 'البنوك' },
        { symbol: '2030', name: 'سابك', sector: 'البتروكيماويات' },
        { symbol: '1180', name: 'الأهلي السعودي', sector: 'البنوك' },
        { symbol: '1211', name: 'معادن', sector: 'المواد الأساسية' },
        { symbol: '7010', name: 'الاتصالات السعودية', sector: 'الاتصالات' },
        { symbol: '2380', name: 'بترو رابغ', sector: 'البتروكيماويات' },
        { symbol: '1140', name: 'البنك الأهلي التجاري', sector: 'البنوك' }
    ];
    
    return mockStocks.map((stock, index) => ({
        ...stock,
        id: index + 1,
        market_cap: Math.random() * 1000000000000
    }));
}

// Display Stocks
function displayStocks(stocks) {
    const stocksGrid = document.getElementById('stocks-grid');
    if (!stocksGrid) return;
    
    stocksGrid.innerHTML = '';
    
    stocks.forEach(stock => {
        const stockCard = createStockCard(stock);
        stocksGrid.appendChild(stockCard);
    });
}

// Create Stock Card
function createStockCard(stock) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => showStockDetails(stock);
    
    // Generate mock price data
    const basePrice = 50 + Math.random() * 100;
    const change = (Math.random() - 0.5) * 10;
    const changePercent = (change / basePrice) * 100;
    
    card.innerHTML = `
        <div class="stock-header">
            <div>
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-name">${stock.name}</div>
            </div>
            <div class="stock-sector">${stock.sector}</div>
        </div>
        <div class="stock-metrics">
            <div class="metric">
                <div class="metric-label">السعر</div>
                <div class="metric-value">${basePrice.toFixed(2)} ريال</div>
            </div>
            <div class="metric">
                <div class="metric-label">التغيير</div>
                <div class="metric-value change ${change >= 0 ? 'positive' : 'negative'}">
                    ${change.toFixed(2)} (${changePercent.toFixed(2)}%)
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Filter Stocks
function filterStocks(searchTerm) {
    if (!searchTerm) {
        displayStocks(currentStocks);
        return;
    }
    
    const filtered = currentStocks.filter(stock => 
        stock.symbol.includes(searchTerm) || 
        stock.name.includes(searchTerm) ||
        stock.sector.includes(searchTerm)
    );
    
    displayStocks(filtered);
}

// Show Stock Details
async function showStockDetails(stock) {
    const modal = document.getElementById('stock-modal');
    const modalTitle = document.getElementById('modal-stock-name');
    const stockDetails = document.getElementById('stock-details');
    
    modalTitle.textContent = `${stock.name} (${stock.symbol})`;
    modal.style.display = 'block';
    
    // Load stock price data
    try {
        const response = await fetch(`${API_BASE}/stocks/${stock.symbol}/price`);
        const data = await response.json();
        
        if (data.success) {
            displayStockDetails(data.data, stockDetails);
        }
    } catch (error) {
        console.error('Error loading stock details:', error);
        // Use mock data
        const mockData = {
            symbol: stock.symbol,
            price: 50 + Math.random() * 100,
            change: (Math.random() - 0.5) * 10,
            volume: Math.floor(Math.random() * 1000000)
        };
        mockData.change_percent = (mockData.change / mockData.price) * 100;
        displayStockDetails(mockData, stockDetails);
    }
    
    // Load stock chart
    loadStockChart(stock.symbol);
}

// Display Stock Details
function displayStockDetails(data, container) {
    container.innerHTML = `
        <div class="stock-detail-grid">
            <div class="detail-item">
                <span class="label">السعر الحالي:</span>
                <span class="value">${data.price.toFixed(2)} ريال</span>
            </div>
            <div class="detail-item">
                <span class="label">التغيير:</span>
                <span class="value change ${data.change >= 0 ? 'positive' : 'negative'}">
                    ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)
                </span>
            </div>
            <div class="detail-item">
                <span class="label">حجم التداول:</span>
                <span class="value">${data.volume ? data.volume.toLocaleString('ar-SA') : 'غير متوفر'}</span>
            </div>
            <div class="detail-item">
                <span class="label">آخر تحديث:</span>
                <span class="value">${new Date().toLocaleString('ar-SA')}</span>
            </div>
        </div>
    `;
}

// Load Stock Chart
async function loadStockChart(symbol) {
    try {
        const response = await fetch(`${API_BASE}/stocks/${symbol}/history?days=30`);
        const data = await response.json();
        
        if (data.success) {
            createStockChart(data.data);
        }
    } catch (error) {
        console.error('Error loading stock chart:', error);
        // Create mock chart data
        const mockData = generateMockChartData(30);
        createStockChart(mockData);
    }
}

// Generate Mock Chart Data
function generateMockChartData(days) {
    const data = [];
    let price = 50 + Math.random() * 50;
    
    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        price += (Math.random() - 0.5) * 5;
        price = Math.max(price, 10);
        
        data.push({
            date: date.toISOString().split('T')[0],
            close: price
        });
    }
    
    return data;
}

// Create Stock Chart
function createStockChart(data) {
    const ctx = document.getElementById('stock-chart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    const labels = data.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('ar-SA', { month: 'short', day: 'numeric' });
    });
    
    const prices = data.map(item => item.close);
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'السعر',
                data: prices,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            }
        }
    });
}

// Close Stock Modal
function closeStockModal() {
    const modal = document.getElementById('stock-modal');
    modal.style.display = 'none';
    
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}

// Load Top Stocks
function loadTopStocks() {
    const topStocksContainer = document.getElementById('top-stocks');
    if (!topStocksContainer) return;
    
    // Mock top performing stocks
    const topStocks = [
        { symbol: '2222', name: 'أرامكو', price: 35.50, change: 2.5 },
        { symbol: '1120', name: 'الراجحي', price: 85.20, change: 1.8 },
        { symbol: '2030', name: 'سابك', price: 95.80, change: -0.5 },
        { symbol: '1180', name: 'الأهلي', price: 42.30, change: 3.2 },
        { symbol: '1211', name: 'معادن', price: 65.40, change: 1.1 }
    ];
    
    topStocksContainer.innerHTML = '';
    
    topStocks.forEach(stock => {
        const stockItem = document.createElement('div');
        stockItem.className = 'stock-item';
        stockItem.innerHTML = `
            <div class="stock-info">
                <h4>${stock.name}</h4>
                <p>${stock.symbol}</p>
            </div>
            <div class="stock-price">
                <div class="price">${stock.price.toFixed(2)} ريال</div>
                <div class="change ${stock.change >= 0 ? 'positive' : 'negative'}">
                    ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
                </div>
            </div>
        `;
        topStocksContainer.appendChild(stockItem);
    });
}

// Load Sectors Chart
function loadSectorsChart() {
    const ctx = document.getElementById('sectorsChart');
    if (!ctx) return;
    
    const sectorsData = {
        labels: ['البنوك', 'الطاقة', 'البتروكيماويات', 'الاتصالات', 'المواد الأساسية', 'أخرى'],
        datasets: [{
            data: [25, 20, 15, 12, 10, 18],
            backgroundColor: [
                '#667eea',
                '#764ba2',
                '#f093fb',
                '#f5576c',
                '#4facfe',
                '#43e97b'
            ],
            borderWidth: 0
        }]
    };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: sectorsData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Load Stock Options for Indicators
function loadStockOptions() {
    const stockSelect = document.getElementById('indicator-stock');
    if (!stockSelect) return;
    
    // Clear existing options
    stockSelect.innerHTML = '<option value="">-- اختر سهم --</option>';
    
    // Add stock options
    currentStocks.forEach(stock => {
        const option = document.createElement('option');
        option.value = stock.symbol;
        option.textContent = `${stock.name} (${stock.symbol})`;
        stockSelect.appendChild(option);
    });
}

// Load Indicators
async function loadIndicators() {
    const stockSymbol = document.getElementById('indicator-stock').value;
    const indicatorType = document.getElementById('indicator-type').value;
    
    if (!stockSymbol) {
        showToast('يرجى اختيار سهم أولاً', 'error');
        return;
    }
    
    showLoading();
    
    try {
        let url = `${API_BASE}/indicators/${stockSymbol}`;
        if (indicatorType !== 'all') {
            url += `/specific`;
        }
        
        let response;
        if (indicatorType === 'all') {
            response = await fetch(url);
        } else {
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    indicator: indicatorType,
                    parameters: {}
                })
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayIndicators(data.data);
            loadSignals(stockSymbol);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error loading indicators:', error);
        showToast('حدث خطأ في تحميل المؤشرات', 'error');
    } finally {
        hideLoading();
    }
}

// Display Indicators
function displayIndicators(data) {
    // Create indicators chart if data is available
    if (data.indicators) {
        createIndicatorsChart(data.indicators);
    }
    
    showToast('تم تحميل المؤشرات بنجاح', 'success');
}

// Create Indicators Chart
function createIndicatorsChart(indicators) {
    const ctx = document.getElementById('indicators-chart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (indicatorsChart) {
        indicatorsChart.destroy();
    }
    
    // Create sample chart with RSI data if available
    let chartData = [];
    let labels = [];
    
    if (indicators.RSI_14) {
        chartData = indicators.RSI_14.slice(-30); // Last 30 points
        labels = Array.from({length: chartData.length}, (_, i) => `يوم ${i + 1}`);
    } else {
        // Generate mock RSI data
        chartData = Array.from({length: 30}, () => 30 + Math.random() * 40);
        labels = Array.from({length: 30}, (_, i) => `يوم ${i + 1}`);
    }
    
    indicatorsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'RSI',
                data: chartData,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            }
        }
    });
}

// Load Signals
async function loadSignals(symbol) {
    try {
        const response = await fetch(`${API_BASE}/indicators/${symbol}/signals`);
        const data = await response.json();
        
        if (data.success) {
            displaySignals(data.data);
        }
    } catch (error) {
        console.error('Error loading signals:', error);
        // Display mock signals
        displaySignals({
            signals: {
                RSI_Signal: 'محايد',
                RSI_Value: 45,
                MACD_Signal: 'إشارة شراء',
                MA_Signal: 'اتجاه صاعد'
            },
            analysis: {
                recommendation: 'شراء',
                confidence: 75,
                reasons: ['MACD يعطي إشارة شراء', 'الاتجاه العام صاعد']
            }
        });
    }
}

// Display Signals
function displaySignals(data) {
    const signalsContainer = document.getElementById('current-signals');
    if (!signalsContainer) return;
    
    const signals = data.signals || {};
    const analysis = data.analysis || {};
    
    let signalsHtml = '<div class="signals-grid">';
    
    // Display individual signals
    Object.keys(signals).forEach(key => {
        if (key.endsWith('_Signal')) {
            const indicatorName = key.replace('_Signal', '');
            const value = signals[key];
            const colorClass = getSignalColorClass(value);
            
            signalsHtml += `
                <div class="signal-item">
                    <div class="signal-name">${getIndicatorDisplayName(indicatorName)}</div>
                    <div class="signal-value ${colorClass}">${value}</div>
                </div>
            `;
        }
    });
    
    signalsHtml += '</div>';
    
    // Display overall analysis
    if (analysis.recommendation) {
        const recommendationClass = getSignalColorClass(analysis.recommendation);
        signalsHtml += `
            <div class="overall-analysis">
                <h4>التحليل الشامل</h4>
                <div class="recommendation ${recommendationClass}">
                    <strong>التوصية: ${analysis.recommendation}</strong>
                    <span class="confidence">مستوى الثقة: ${analysis.confidence}%</span>
                </div>
                <div class="reasons">
                    <strong>الأسباب:</strong>
                    <ul>
                        ${analysis.reasons ? analysis.reasons.map(reason => `<li>${reason}</li>`).join('') : ''}
                    </ul>
                </div>
            </div>
        `;
    }
    
    signalsContainer.innerHTML = signalsHtml;
}

// Get Signal Color Class
function getSignalColorClass(signal) {
    const lowerSignal = signal.toLowerCase();
    if (lowerSignal.includes('شراء') || lowerSignal.includes('صاعد')) {
        return 'positive';
    } else if (lowerSignal.includes('بيع') || lowerSignal.includes('هابط')) {
        return 'negative';
    } else {
        return 'neutral';
    }
}

// Get Indicator Display Name
function getIndicatorDisplayName(indicator) {
    const names = {
        'RSI': 'مؤشر القوة النسبية',
        'MACD': 'MACD',
        'MA': 'المتوسطات المتحركة',
        'BB': 'نطاقات بولينجر'
    };
    return names[indicator] || indicator;
}

// Load Popular Indicators
async function loadPopularIndicators() {
    try {
        const response = await fetch(`${API_BASE}/indicators/popular`);
        const data = await response.json();
        
        if (data.success) {
            displayPopularIndicators(data.data);
        }
    } catch (error) {
        console.error('Error loading popular indicators:', error);
        // Display mock data
        displayPopularIndicators({
            trend_indicators: [
                { name: 'المتوسط المتحرك البسيط', code: 'SMA', description: 'يحسب متوسط الأسعار خلال فترة زمنية محددة' },
                { name: 'MACD', code: 'MACD', description: 'مؤشر تقارب وتباعد المتوسطات المتحركة' }
            ],
            momentum_indicators: [
                { name: 'مؤشر القوة النسبية', code: 'RSI', description: 'يقيس قوة حركة السعر' }
            ]
        });
    }
}

// Display Popular Indicators
function displayPopularIndicators(data) {
    const container = document.getElementById('popular-indicators');
    if (!container) return;
    
    let html = '';
    
    Object.keys(data).forEach(category => {
        const categoryName = getCategoryDisplayName(category);
        html += `<div class="indicator-category">
            <h4>${categoryName}</h4>
            <div class="indicator-list">`;
        
        data[category].forEach(indicator => {
            html += `
                <div class="indicator-item">
                    <div class="indicator-name">${indicator.name}</div>
                    <div class="indicator-code">${indicator.code}</div>
                    <div class="indicator-description">${indicator.description}</div>
                </div>
            `;
        });
        
        html += '</div></div>';
    });
    
    container.innerHTML = html;
}

// Get Category Display Name
function getCategoryDisplayName(category) {
    const names = {
        'trend_indicators': 'مؤشرات الاتجاه',
        'momentum_indicators': 'مؤشرات الزخم',
        'volatility_indicators': 'مؤشرات التقلب',
        'volume_indicators': 'مؤشرات الحجم'
    };
    return names[category] || category;
}

// Apply Strategy
function applyStrategy(strategyType) {
    showLoading();
    
    // Simulate strategy application
    setTimeout(() => {
        const results = generateStrategyResults(strategyType);
        displayStrategyResults(results);
        hideLoading();
        showToast(`تم تطبيق استراتيجية ${getStrategyDisplayName(strategyType)}`, 'success');
    }, 2000);
}

// Generate Strategy Results
function generateStrategyResults(strategyType) {
    const strategies = {
        'moving_average': {
            name: 'استراتيجية المتوسطات المتحركة',
            signals: [
                { stock: 'أرامكو (2222)', signal: 'شراء', confidence: 85 },
                { stock: 'الراجحي (1120)', signal: 'انتظار', confidence: 60 },
                { stock: 'سابك (2030)', signal: 'بيع', confidence: 75 }
            ],
            performance: {
                total_signals: 15,
                successful: 10,
                success_rate: 67
            }
        },
        'rsi': {
            name: 'استراتيجية RSI',
            signals: [
                { stock: 'الأهلي (1180)', signal: 'شراء', confidence: 90 },
                { stock: 'معادن (1211)', signal: 'شراء', confidence: 80 },
                { stock: 'الاتصالات (7010)', signal: 'محايد', confidence: 55 }
            ],
            performance: {
                total_signals: 12,
                successful: 9,
                success_rate: 75
            }
        },
        'macd': {
            name: 'استراتيجية MACD',
            signals: [
                { stock: 'بترو رابغ (2380)', signal: 'بيع', confidence: 85 },
                { stock: 'الأهلي التجاري (1140)', signal: 'شراء', confidence: 70 }
            ],
            performance: {
                total_signals: 8,
                successful: 5,
                success_rate: 63
            }
        }
    };
    
    return strategies[strategyType] || strategies['moving_average'];
}

// Display Strategy Results
function displayStrategyResults(results) {
    const resultsContainer = document.getElementById('strategy-results');
    const contentContainer = document.getElementById('strategy-content');
    
    if (!resultsContainer || !contentContainer) return;
    
    let html = `
        <div class="strategy-info">
            <h4>${results.name}</h4>
            <div class="performance-metrics">
                <div class="metric">
                    <span class="label">إجمالي الإشارات:</span>
                    <span class="value">${results.performance.total_signals}</span>
                </div>
                <div class="metric">
                    <span class="label">الإشارات الناجحة:</span>
                    <span class="value">${results.performance.successful}</span>
                </div>
                <div class="metric">
                    <span class="label">معدل النجاح:</span>
                    <span class="value">${results.performance.success_rate}%</span>
                </div>
            </div>
        </div>
        
        <div class="strategy-signals">
            <h4>الإشارات الحالية</h4>
            <div class="signals-list">
    `;
    
    results.signals.forEach(signal => {
        const signalClass = getSignalColorClass(signal.signal);
        html += `
            <div class="signal-row">
                <div class="signal-stock">${signal.stock}</div>
                <div class="signal-action ${signalClass}">${signal.signal}</div>
                <div class="signal-confidence">${signal.confidence}%</div>
            </div>
        `;
    });
    
    html += '</div></div>';
    
    contentContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
}

// Get Strategy Display Name
function getStrategyDisplayName(strategyType) {
    const names = {
        'moving_average': 'المتوسطات المتحركة',
        'rsi': 'RSI',
        'macd': 'MACD'
    };
    return names[strategyType] || strategyType;
}

// Utility Functions
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'flex';
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

