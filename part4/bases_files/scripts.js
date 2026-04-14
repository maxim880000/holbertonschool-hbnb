/* =========================================
   HBnB - Client-Side Scripts
   ES6 - Fetch API - JWT via Cookies
   ========================================= */

const API_URL = '';

/* =========================================
   Cookie utilities
   ========================================= */

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
}

/* =========================================
   XSS protection
   ========================================= */

function escapeHtml(str) {
    if (typeof str !== 'string') return String(str ?? '');
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/* =========================================
   Stars rendering
   ========================================= */

function renderStars(rating) {
    const n = Math.min(5, Math.max(1, parseInt(rating) || 1));
    return `<p class="rating">${'&#9733;'.repeat(n)}${'&#9734;'.repeat(5 - n)}</p>`;
}

/* =========================================
   URL query param
   ========================================= */

function getQueryParam(key) {
    return new URLSearchParams(window.location.search).get(key);
}

/* =========================================
   Amenity icon mapping (provided images)
   ========================================= */

function getAmenityIcon(name) {
    const n = name.toLowerCase();
    if (n.includes('wifi') || n.includes('wi-fi') || n.includes('internet')) return 'images/wifi.png';
    if (n.includes('shower') || n.includes('bath')) return 'images/shower.png';
    if (n.includes('bed') || n.includes('room') || n.includes('sleep')) return 'images/bed.png';
    return null;
}

/* =========================================
   Nav auth helper
   Show/hide login link + user info + logout
   ========================================= */

function updateNavAuth(token) {
    const loginLink = document.getElementById('login-link');
    const userInfo  = document.getElementById('user-info');
    const userNameEl = document.getElementById('user-name');
    const logoutLink = document.getElementById('logout-link');

    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (userInfo)  userInfo.style.display  = 'flex';
        if (userNameEl) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                userNameEl.textContent = payload.email || payload.first_name || 'User';
            } catch {
                userNameEl.textContent = 'User';
            }
        }
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                document.cookie = 'token=; path=/; max-age=0';
                window.location.href = 'index.html';
            });
        }
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (userInfo)  userInfo.style.display  = 'none';
    }
}

/* =========================================
   TASK 1 — Login page
   POST credentials → store JWT cookie → redirect
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        await loginUser(
            document.getElementById('email').value.trim(),
            document.getElementById('password').value
        );
    });
});

async function loginUser(email, password) {
    if (!email || !password) {
        alert('Please fill in all fields.');
        return;
    }
    try {
        const response = await fetch(`${API_URL}/api/v1/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = 'index.html';
        } else {
            const data = await response.json().catch(() => ({}));
            alert(data.message || data.error || 'Login failed: ' + response.statusText);
        }
    } catch {
        alert('Unable to reach the server. Please try again later.');
    }
}

/* =========================================
   TASK 2 — Index page
   Check auth → show/hide login → fetch places → filter
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('places-list')) return;

    const token = getCookie('token');
    updateNavAuth(token);

    if (token) {
        fetchPlaces(token);
    } else {
        document.getElementById('places-list').innerHTML =
            '<p style="text-align:center;color:#888;padding:2rem;">Please <a href="login.html" style="color:#ff5a5f;font-weight:600;">login</a> to see places.</p>';
    }

    document.getElementById('price-filter').addEventListener('change', (event) => {
        const selected = event.target.value;
        document.querySelectorAll('.place-card').forEach((card) => {
            const price = parseFloat(card.dataset.price);
            card.style.display =
                (selected === 'all' || price <= parseFloat(selected)) ? 'flex' : 'none';
        });
    });
});

async function fetchPlaces(token) {
    const container = document.getElementById('places-list');
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/api/v1/places/`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const places = await response.json();

        // Fetch detailed data (price) for each place in parallel
        const detailed = await Promise.all(
            places.map((p) =>
                fetch(`${API_URL}/api/v1/places/${p.id}`, {
                    headers: { Authorization: `Bearer ${token}` },
                })
                    .then((r) => (r.ok ? r.json() : p))
                    .catch(() => p)
            )
        );

        displayPlaces(detailed);
    } catch {
        container.innerHTML =
            '<p style="text-align:center;color:#888;padding:2rem;">Failed to load places. Check the API is running.</p>';
    }
}

function displayPlaces(places) {
    const container = document.getElementById('places-list');
    if (!container) return;
    container.innerHTML = '';

    if (!places || places.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#888;padding:2rem;">No places available.</p>';
        return;
    }

    places.forEach((place) => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.dataset.price = place.price || 0;

        const price = place.price !== undefined ? `$${place.price}` : 'N/A';

        card.innerHTML = `
            <h2>${escapeHtml(place.title)}</h2>
            <p>Price: <strong>${price}/night</strong></p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        container.appendChild(card);
    });
}

/* =========================================
   TASK 3 — Place details page
   Fetch place → display info + reviews
   Show #add-review section only if authenticated
   Handle inline review form submission
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('place-details')) return;

    const placeId = getQueryParam('id');
    if (!placeId) { window.location.href = 'index.html'; return; }

    const token = getCookie('token');
    updateNavAuth(token);

    // Show/hide the inline add-review section
    const addReviewSection = document.getElementById('add-review');
    if (addReviewSection) {
        addReviewSection.style.display = token ? 'block' : 'none';
    }

    fetchPlaceDetails(placeId, token);

    // Wire up the inline review form
    const reviewForm = document.getElementById('review-form');
    if (reviewForm && token) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitReview(token, placeId);
        });
    }
});

async function fetchPlaceDetails(placeId, token) {
    const detailsContainer  = document.getElementById('place-details');
    const reviewsContainer  = document.getElementById('reviews');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
        const response = await fetch(`${API_URL}/api/v1/places/${placeId}`, { headers });
        if (!response.ok) {
            detailsContainer.innerHTML = '<p style="color:#888;">Place not found.</p>';
            return;
        }

        const place = await response.json();

        const amenitiesHtml = place.amenities && place.amenities.length > 0
            ? `<div class="amenities-list">${place.amenities.map((a) => {
                const icon = getAmenityIcon(a.name);
                const iconImg = icon
                    ? `<img src="${icon}" alt="" style="width:16px;height:16px;object-fit:contain;">`
                    : '';
                return `<span class="amenity-tag">${iconImg}${escapeHtml(a.name)}</span>`;
            }).join('')}</div>`
            : '<p style="color:#888;">No amenities listed.</p>';

        const ownerName = place.owner
            ? `${escapeHtml(place.owner.first_name)} ${escapeHtml(place.owner.last_name)}`
            : 'Unknown';

        detailsContainer.innerHTML = `
            <div class="place-details">
                <h2>${escapeHtml(place.title)}</h2>
                <div class="place-info">
                    <span><strong>Host:</strong> ${ownerName}</span>
                    <span><strong>Price:</strong> $${place.price}/night</span>
                    <span><strong>Location:</strong> ${place.latitude.toFixed(4)}, ${place.longitude.toFixed(4)}</span>
                    <span><strong>Description:</strong> ${escapeHtml(place.description || 'No description.')}</span>
                </div>
                <h3 style="margin-top:1rem;margin-bottom:0.5rem;">Amenities</h3>
                ${amenitiesHtml}
            </div>
        `;

        await fetchReviews(placeId, reviewsContainer, headers);
    } catch {
        detailsContainer.innerHTML = '<p style="color:#888;">Failed to load place details.</p>';
    }
}

async function fetchReviews(placeId, container, headers) {
    if (!container) return;

    try {
        const response = await fetch(
            `${API_URL}/api/v1/reviews/places/${placeId}/reviews`,
            { headers }
        );

        if (!response.ok) {
            container.innerHTML = '<h3>Reviews</h3><p style="color:#888;">Could not load reviews.</p>';
            return;
        }

        const reviews = await response.json();

        if (!reviews || reviews.length === 0) {
            container.innerHTML = '<h3>Reviews</h3><p style="color:#888;">No reviews yet. Be the first!</p>';
            return;
        }

        const reviewsHtml = reviews.map((r) => `
            <div class="review-card">
                <p class="reviewer">${escapeHtml(r.user_id || 'Anonymous')}</p>
                ${renderStars(r.rating)}
                <p class="comment">${escapeHtml(r.comment)}</p>
            </div>
        `).join('');

        container.innerHTML = `<h3>Reviews (${reviews.length})</h3>${reviewsHtml}`;
    } catch {
        container.innerHTML = '<h3>Reviews</h3><p style="color:#888;">Failed to load reviews.</p>';
    }
}

/* =========================================
   TASK 4 — Add review page (standalone)
   Redirect if not authenticated
   POST review → redirect back to place
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    // Only runs on add_review.html (no #place-details element)
    if (document.getElementById('place-details')) return;

    const reviewForm = document.getElementById('review-form');
    if (!reviewForm) return;

    const token = getCookie('token');
    if (!token) { window.location.href = 'index.html'; return; }

    const placeId = getQueryParam('id');
    if (!placeId) { window.location.href = 'index.html'; return; }

    updateNavAuth(token);

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        await submitReview(token, placeId);
    });
});

/* =========================================
   Shared review submission (place.html + add_review.html)
   ========================================= */

async function submitReview(token, placeId) {
    const reviewEl = document.getElementById('review');
    const comment  = reviewEl ? reviewEl.value.trim() : '';
    const rating   = parseInt(document.getElementById('rating').value, 10);

    if (!comment) { alert('Please write your review.'); return; }
    if (!rating || rating < 1 || rating > 5) { alert('Please select a rating.'); return; }

    let userId = null;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        userId = payload.sub;
    } catch {
        alert('Session error. Please log in again.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/v1/reviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ comment, rating, place_id: placeId, user_id: userId }),
        });

        if (response.ok) {
            alert('Review submitted successfully!');
            document.getElementById('review-form').reset();
            window.location.href = `place.html?id=${placeId}`;
        } else {
            const data = await response.json().catch(() => ({}));
            alert(data.message || data.error || 'Failed to submit review.');
        }
    } catch {
        alert('Unable to reach the server. Please try again later.');
    }
}
