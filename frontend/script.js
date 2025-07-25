function slugify(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

let loadingInterval = null;
let loadingStart = null;
let loadingMsgInterval = null;
const loadingMessages = [
    'Yükleniyor...',
    'AI analizi yapılıyor...',
    'Filmler bulunuyor...',
    'En iyi öneriler hazırlanıyor...'
];

document.getElementById('filmForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const filmAdi = document.getElementById('filmAdi').value;
    const sonuclarDiv = document.getElementById('sonuclar');
    const loadingArea = document.getElementById('loading-area');
    // Önceki intervali temizle
    if (loadingInterval) clearInterval(loadingInterval);
    if (loadingMsgInterval) clearInterval(loadingMsgInterval);
    let msgIndex = 0;
    loadingArea.innerHTML = `<em id="loading-msg">${loadingMessages[0]} <span id='loading-seconds'>0</span> sn</em>`;
    sonuclarDiv.innerHTML = '';
    loadingStart = Date.now();
    loadingInterval = setInterval(() => {
        const el = document.getElementById('loading-seconds');
        if (el) {
            const elapsed = Math.floor((Date.now() - loadingStart) / 1000);
            el.textContent = elapsed;
        }
    }, 200);
    loadingMsgInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % loadingMessages.length;
        const msgEl = document.getElementById('loading-msg');
        if (msgEl) {
            msgEl.innerHTML = `${loadingMessages[msgIndex]} <span id='loading-seconds'>${Math.floor((Date.now() - loadingStart) / 1000)}</span> sn`;
        }
    }, 1800);
    let totalElapsed = 0;
    try {
        const response = await fetch('https://film-neri-modeli.zeabur.app/api/oner', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filmAdi })
        });
        const data = await response.json();
        if (loadingInterval) clearInterval(loadingInterval);
        if (loadingMsgInterval) clearInterval(loadingMsgInterval);
        totalElapsed = Math.floor((Date.now() - loadingStart) / 1000);
        if (response.ok) {
            let userFilm = {
                name: filmAdi,
                theme: Array.isArray(data.user_film_theme) && data.user_film_theme.length > 0 ? data.user_film_theme : ['Tema bilgisi alınamadı'],
                poster_url: data.user_film_poster || ''
            };
            let otherFilms = [];
            if (data.oneriler && data.oneriler.length > 0) {
                const lowerFilmAdi = filmAdi.trim().toLowerCase();
                data.oneriler.forEach(film => {
                    if (film.name.trim().toLowerCase() !== lowerFilmAdi) {
                        otherFilms.push(film);
                    }
                });
            }
            let html = '';
            if (userFilm) {
                html += `<div class='user-film-block'>
                    <h2>Senin yazdığın film</h2>
                    <div class="film-card" style="margin-bottom:24px;max-width:340px;margin-left:auto;margin-right:auto;">
                        <img src="${userFilm.poster_url || 'https://placehold.co/120x180?text=No+Image'}" alt="${userFilm.name} posteri" class="film-poster" onerror="this.onerror=null;this.src='https://placehold.co/120x180?text=No+Image';" width="120" height="180">
                        <div class="film-title">${userFilm.name}</div>
                        <div class="film-temalar">
                            <div class="film-theme-label">Temalar</div>
                            ${userFilm.theme.map(t => `<span class='film-theme-tag'>${t}</span>`).join('')}
                        </div>
                    </div>
                </div>`;
            }
            html += `<h2>Önerilen Filmler</h2><ul>`;
            otherFilms.forEach(film => {
                const slug = slugify(film.name);
                const link = `https://letterboxd.com/film/${slug}/`;
                const poster = film.poster_url || 'https://placehold.co/120x180?text=No+Image';
                html += `<li class="film-card">
                    <img src="${poster}" alt="${film.name} posteri" class="film-poster" onerror="this.onerror=null;this.src='https://placehold.co/120x180?text=No+Image';" width="120" height="180">
                    <div class="film-title">${film.name}</div>
                    <div class="film-temalar">
                        <div class="film-theme-label">Temalar</div>
                        ${film.theme.map(t => `<span class='film-theme-tag'>${t}</span>`).join('')}
                    </div>
                    <div class="film-link"><a href="${link}" target="_blank">Letterboxd'da aç</a></div>
                </li>`;
            });
            html += '</ul>';
            sonuclarDiv.innerHTML = html;
            loadingArea.innerHTML = `<span id="loading-msg" style="color:#fff;">Öneriler ${totalElapsed} sn'de yüklendi.</span>`;
        } else {
            loadingArea.innerHTML = '';
            sonuclarDiv.innerHTML = `<span style='color:red'>${data.error || 'Bir hata oluştu.'}</span>`;
        }
    } catch (err) {
        if (loadingInterval) clearInterval(loadingInterval);
        if (loadingMsgInterval) clearInterval(loadingMsgInterval);
        loadingArea.innerHTML = '';
        sonuclarDiv.innerHTML = `<span style='color:red'>Sunucuya bağlanılamadı.</span>`;
    }
}); 