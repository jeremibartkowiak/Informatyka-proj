// SmartTravel - Client-side SPA Application Logic

const API_BASE = '/api';

// State Management
let jwtToken = localStorage.getItem('jwtToken') || null;
let userEmail = localStorage.getItem('userEmail') || null;

// Countries Configuration
const COUNTRIES_DATA = [
    { name: 'Poland', flag: '🇵🇱', sub: 'Europe • Currency: PLN' },
    { name: 'Spain', flag: '🇪🇸', sub: 'Europe • Currency: EUR' },
    { name: 'Germany', flag: '🇩🇪', sub: 'Europe • Currency: EUR' },
    { name: 'France', flag: '🇫🇷', sub: 'Europe • Currency: EUR' },
    { name: 'Italy', flag: '🇮🇹', sub: 'Europe • Currency: EUR' },
    { name: 'United Kingdom', flag: '🇬🇧', sub: 'Europe • Currency: GBP' },
    { name: 'United States', flag: '🇺🇸', sub: 'North America • Currency: USD' },
    { name: 'Canada', flag: '🇨🇦', sub: 'North America • Currency: CAD' },
    { name: 'Japan', flag: '🇯🇵', sub: 'Asia • Currency: JPY' },
    { name: 'China', flag: '🇨🇳', sub: 'Asia • Currency: CNY' },
    { name: 'Australia', flag: '🇦🇺', sub: 'Oceania • Currency: AUD' },
    { name: 'Egypt', flag: '🇪🇬', sub: 'Africa • Currency: EGP' },
    { name: 'Greece', flag: '🇬🇷', sub: 'Europe • Currency: EUR' },
    { name: 'Turkey', flag: '🇹🇷', sub: 'Europe/Asia • Currency: TRY' },
    { name: 'Croatia', flag: '🇭🇷', sub: 'Europe • Currency: EUR' },
    { name: 'Czechia', flag: '🇨🇿', sub: 'Europe • Currency: CZK' },
    { name: 'Slovakia', flag: '🇸🇰', sub: 'Europe • Currency: EUR' },
    { name: 'Norway', flag: '🇳🇴', sub: 'Europe • Currency: NOK' },
    { name: 'Sweden', flag: '🇸🇪', sub: 'Europe • Currency: SEK' },
    { name: 'Netherlands', flag: '🇳🇱', sub: 'Europe • Currency: EUR' },
    { name: 'Switzerland', flag: '🇨🇭', sub: 'Europe • Currency: CHF' },
    { name: 'Austria', flag: '🇦🇹', sub: 'Europe • Currency: EUR' },
    { name: 'Portugal', flag: '🇵🇹', sub: 'Europe • Currency: EUR' },
    { name: 'Ukraine', flag: '🇺🇦', sub: 'Europe • Currency: UAH' },
    { name: 'Brazil', flag: '🇧🇷', sub: 'South America • Currency: BRL' },
    { name: 'Mexico', flag: '🇲🇽', sub: 'North America • Currency: MXN' },
    { name: 'Argentina', flag: '🇦🇷', sub: 'South America • Currency: ARS' },
    { name: 'India', flag: '🇮🇳', sub: 'Asia • Currency: INR' },
    { name: 'South Korea', flag: '🇰🇷', sub: 'Asia • Currency: KRW' },
    { name: 'Thailand', flag: '🇹🇭', sub: 'Asia • Currency: THB' },
    { name: 'Vietnam', flag: '🇻🇳', sub: 'Asia • Currency: VND' },
    { name: 'United Arab Emirates', flag: '🇦🇪', sub: 'Middle East • Currency: AED' },
    { name: 'Iceland', flag: '🇮🇸', sub: 'Europe • Currency: ISK' },
    { name: 'Finland', flag: '🇫🇮', sub: 'Europe • Currency: EUR' },
    { name: 'Denmark', flag: '🇩🇰', sub: 'Europe • Currency: DKK' },
    { name: 'Ireland', flag: '🇮🇪', sub: 'Europe • Currency: EUR' },
    { name: 'Belgium', flag: '🇧🇪', sub: 'Europe • Currency: EUR' }
];

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    checkUrlForActivationToken();
    initCustomDropdown();
    checkAuthStatus();
});

// Custom Dropdown Component Logic
function initCustomDropdown() {
    renderDropdownOptions(COUNTRIES_DATA);

    document.addEventListener('click', (e) => {
        const wrapper = document.getElementById('custom-select-wrapper');
        if (wrapper && !wrapper.contains(e.target)) {
            const dropdown = document.getElementById('custom-select-dropdown');
            if (dropdown) dropdown.classList.add('hidden');
        }
    });
}

function renderDropdownOptions(items) {
    const container = document.getElementById('dropdown-options-container');
    if (!container) return;

    container.innerHTML = '';
    const currentVal = getSelectedCountry();

    items.forEach(c => {
        const div = document.createElement('div');
        div.className = `dropdown-option-item ${c.name === currentVal ? 'selected' : ''}`;
        div.onclick = (e) => {
            e.stopPropagation();
            selectCountryOption(c.name, c.flag);
        };
        div.innerHTML = `
            <span class="option-flag emoji">${c.flag}</span>
            <div class="option-info">
                <span class="option-name">${escapeHtml(c.name)}</span>
                <span class="option-sub">${escapeHtml(c.sub)}</span>
            </div>
            ${c.name === currentVal ? '<span class="option-check">✓</span>' : ''}
        `;
        container.appendChild(div);
    });

    if (items.length === 0) {
        container.innerHTML = '<div class="dropdown-no-results">Nie znaleziono takiego kraju.</div>';
    }
}

function toggleCustomDropdown(e) {
    if (e) e.stopPropagation();
    const dropdown = document.getElementById('custom-select-dropdown');
    if (!dropdown) return;

    const isHidden = dropdown.classList.contains('hidden');
    if (isHidden) {
        dropdown.classList.remove('hidden');
        const filterInput = document.getElementById('dropdown-filter-input');
        if (filterInput) {
            filterInput.value = '';
            filterInput.focus();
            renderDropdownOptions(COUNTRIES_DATA);
        }
    } else {
        dropdown.classList.add('hidden');
    }
}

function filterCountryOptions(e) {
    const query = (e.target.value || '').toLowerCase().trim();
    const filtered = COUNTRIES_DATA.filter(c => 
        c.name.toLowerCase().includes(query) || c.sub.toLowerCase().includes(query)
    );
    renderDropdownOptions(filtered);
}

function selectCountryOption(countryName, flagEmoji) {
    const found = COUNTRIES_DATA.find(c => c.name.toLowerCase() === (countryName || '').toLowerCase());
    const finalFlag = flagEmoji || (found ? found.flag : '🌍');
    const finalName = found ? found.name : countryName;

    const hiddenInput = document.getElementById('country-select');
    if (hiddenInput) hiddenInput.value = finalName;

    const flagEl = document.getElementById('selected-flag');
    const nameEl = document.getElementById('selected-country-name');
    if (flagEl) flagEl.textContent = finalFlag;
    if (nameEl) nameEl.textContent = finalName;

    const dropdown = document.getElementById('custom-select-dropdown');
    if (dropdown) dropdown.classList.add('hidden');

    loadDashboardData(finalName);
}

function getSelectedCountry() {
    const input = document.getElementById('country-select');
    return input ? input.value : 'Polska';
}

// Switch Auth Tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));

    const activeTabBtn = document.getElementById(`tab-${tabName}`);
    const activeForm = document.getElementById(`${tabName}-form`);

    if (activeTabBtn && activeForm) {
        activeTabBtn.classList.add('active');
        activeForm.classList.add('active');
    }
}

// Check URL Query string for email confirmation token
function checkUrlForActivationToken() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
        switchTab('activate');
        document.getElementById('activate-token').value = token;
        showAlert('Wykryto token aktywacyjny z linku e-mail. Kliknij "Aktywuj Konto".', 'info');
    }
}

// Check if user is logged in
function checkAuthStatus() {
    const authSection = document.getElementById('auth-section');
    const dashboardSection = document.getElementById('dashboard-section');
    const statusBar = document.getElementById('user-status-bar');
    const emailDisplay = document.getElementById('user-email-display');

    if (jwtToken) {
        authSection.classList.add('hidden');
        dashboardSection.classList.remove('hidden');
        statusBar.classList.remove('hidden');
        emailDisplay.textContent = userEmail || 'Zalogowany użytkownik';

        // Load initial dashboard data
        const initialCountry = getSelectedCountry();
        loadDashboardData(initialCountry);
    } else {
        authSection.classList.remove('hidden');
        dashboardSection.classList.add('hidden');
        statusBar.classList.add('hidden');
    }
}

// Handler: Registration
async function handleRegister(event) {
    event.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            
            if (result.activationLink) {
                const token = result.activationLink.split('token=')[1];
                if (token) {
                    document.getElementById('activate-token').value = token;
                    setTimeout(() => switchTab('activate'), 1500);
                }
            }
        } else {
            showAlert(result.message || 'Błąd rejestracji.', 'error');
        }
    } catch (err) {
        showAlert('Wystąpił błąd połączenia z serwerem.', 'error');
    }
}

// Handler: Email Activation
async function handleActivate(event) {
    event.preventDefault();
    const token = document.getElementById('activate-token').value.trim();

    try {
        const response = await fetch(`${API_BASE}/auth/confirm-email?token=${encodeURIComponent(token)}`);
        const result = await response.json();

        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            setTimeout(() => switchTab('login'), 1500);
        } else {
            showAlert(result.message || 'Błąd weryfikacji tokenu.', 'error');
        }
    } catch (err) {
        showAlert('Nie udało się zweryfikować tokena.', 'error');
    }
}

// Handler: Login
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();

        if (response.ok && result.success && result.token) {
            jwtToken = result.token;
            userEmail = result.email || email;

            localStorage.setItem('jwtToken', jwtToken);
            localStorage.setItem('userEmail', userEmail);

            showAlert('Zalogowano pomyślnie!', 'success');
            checkAuthStatus();
        } else {
            showAlert(result.message || 'Niepoprawne dane logowania.', 'error');
        }
    } catch (err) {
        showAlert('Błąd serwera podczas logowania.', 'error');
    }
}

// Handler: Logout
document.getElementById('logout-btn')?.addEventListener('click', () => {
    jwtToken = null;
    userEmail = null;
    localStorage.removeItem('jwtToken');
    localStorage.removeItem('userEmail');
    showAlert('Zostałeś wylogowany.', 'info');
    checkAuthStatus();
});

// Handlers attached to Window
window.toggleCustomDropdown = toggleCustomDropdown;
window.filterCountryOptions = filterCountryOptions;
window.selectCountryOption = selectCountryOption;
window.handleSearch = function(event) {
    if (event) event.preventDefault();
    const country = getSelectedCountry();
    if (country) {
        loadDashboardData(country);
    }
};
window.handleCountryChange = function(event) {
    const val = event.target ? event.target.value : event;
    if (val) {
        selectCountryOption(val);
    }
};
window.quickSearch = function(countryName) {
    selectCountryOption(countryName);
};

// Load Dashboard Data from Backend
async function loadDashboardData(countryName) {
    const submitBtn = document.querySelector('#search-form button[type="submit"]');
    const cards = document.querySelectorAll('.dashboard-card');

    // Enable loading UI
    cards.forEach(card => card.classList.add('loading'));
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span><span class="spinner-sm"></span> Wczytywanie...</span>`;
    }

    try {
        const response = await fetch(`${API_BASE}/dashboard/destination?country=${encodeURIComponent(countryName)}`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });

        if (response.status === 401) {
            showAlert('Sesja wygasła. Zaloguj się ponownie.', 'error');
            document.getElementById('logout-btn').click();
            return;
        }

        const data = await response.json();

        if (data && data.geoData) {
            renderDashboard(data);
        } else {
            showAlert('Nie znaleziono danych dla podanego kraju.', 'error');
        }
    } catch (err) {
        showAlert('Wystąpił błąd podczas pobierania danych z API.', 'error');
    } finally {
        // Remove loading UI
        cards.forEach(card => card.classList.remove('loading'));
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span><span class="emoji">📊</span> Pobierz Dane Kraju</span>`;
        }
    }
}

// Render Dashboard Data (Geo, Currency, Weather)
function renderDashboard(data) {
    const geo = data.geoData;
    const curr = data.currencyData;
    const weather = data.weatherData;

    // 1. API Geo (REST Countries)
    document.getElementById('geo-country-name').textContent = geo.name;
    document.getElementById('geo-official-name').textContent = geo.officialName;
    document.getElementById('geo-flag-emoji').textContent = geo.flagEmoji || '🌍';
    document.getElementById('geo-capital').textContent = geo.capital;
    document.getElementById('geo-population').textContent = geo.population.toLocaleString();
    document.getElementById('geo-region').textContent = geo.region;
    document.getElementById('geo-currency').textContent = `${geo.currencyCode} (${geo.currencySymbol})`;

    // 2. API Currency (NBP API)
    document.getElementById('currency-code-display').textContent = `${geo.currencyCode} ➔ PLN`;
    if (curr) {
        document.getElementById('currency-rate').textContent = `${curr.rateToPln.toFixed(4)} PLN`;
        document.getElementById('currency-date').textContent = `Data: ${curr.rateDate}`;
        document.getElementById('currency-note').textContent = curr.note;
    }

    // 3. API Weather (Open-Meteo API)
    document.getElementById('weather-location').textContent = geo.capital;
    if (weather) {
        document.getElementById('weather-temp').textContent = `${weather.temperatureC.toFixed(1)}°C`;
        document.getElementById('weather-desc').textContent = weather.weatherDescription;
        document.getElementById('weather-wind').textContent = `${weather.windSpeedKmh.toFixed(1)} km/h`;
    }
}

// Load Search History from SQL DB
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/history`, {
            headers: { 'Authorization': `Bearer ${jwtToken}` }
        });

        if (response.ok) {
            const logs = await response.json();
            const tbody = document.getElementById('history-table-body');
            tbody.innerHTML = '';

            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center">Brak zapytań w historii.</td></tr>';
                return;
            }

            logs.forEach(log => {
                const date = new Date(log.searchedAt).toLocaleString('pl-PL');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${log.id}</td>
                    <td><strong>${escapeHtml(log.query)}</strong></td>
                    <td>${date}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error('Nie udało się pobrać historii.', err);
    }
}

// Helpers
function showAlert(message, type = 'info') {
    const banner = document.getElementById('alert-banner');
    const msg = document.getElementById('alert-message');

    banner.className = `alert-banner ${type}`;
    msg.textContent = message;
    banner.classList.remove('hidden');

    setTimeout(() => {
        banner.classList.add('hidden');
    }, 6000);
}

function closeAlert() {
    document.getElementById('alert-banner').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
