/* =========================================
   HBnB - Client-Side Scripts
   ES6 - Fetch API - JWT via Cookies
   ========================================= */

const API_URL = 'http://localhost:5000';

/* =========================================
   Cookie utilities
   ========================================= */

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
}

/* =========================================
   XSS protection helper
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
   Stars rendering helper
   ========================================= */

function renderStars(rating) {
    const full = '&#9733;'.repeat(rating);
    const empty = '&#9734;'.repeat(5 - rating);
    return `<span class="rating">${full}${empty}</span>`;
}

/* =========================================
   Amenity icon helper — maps name to image
   ========================================= */

const PLACE_IMAGES = ['images/image.png', 'images/image copy.png'];

function getAmenityIcon(name) {
    const n = name.toLowerCase();
    if (n.includes('wifi') || n.includes('wi-fi') || n.includes('internet')) return 'images/wifi.png';
    if (n.includes('shower') || n.includes('bath')) return 'images/shower.png';
    if (n.includes('bed') || n.includes('room') || n.includes('sleep')) return 'images/bed.png';
    return null;
}

/* =========================================
   URL query param helper
   ========================================= */

function getQueryParam(key) {
    return new URLSearchParams(window.location.search).get(key);
}

/* =========================================
   TASK 1 — Login page
   POST credentials → store JWT cookie → redirect
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await loginUser(
                document.getElementById('email').value.trim(),
                document.getElementById('password').value
            );
        });
    }
});

async function loginUser(email, password) {
    const messageEl = document.getElementById('login-message');

    if (!email || !password) {
        showMessage(messageEl, 'Please fill in all fields.', 'error');
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
            showMessage(
                messageEl,
                data.message || data.error || 'Login failed: ' + response.statusText,
                'error'
            );
        }
    } catch (err) {
        showMessage(messageEl, 'Unable to reach the server. Please try again later.', 'error');
    }
}

/* =========================================
   TASK 2 — Index page
   Check auth → show/hide login link → fetch places
   ========================================= */

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

async function fetchPlaces(token) {
    const container = document.getElementById('places-list');
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/api/v1/places/`, {
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const places = await response.json();

        // List endpoint returns minimal data (no price); fetch details in parallel
        const detailRequests = places.map((p) =>
            fetch(`${API_URL}/api/v1/places/${p.id}`, {
                headers: { Authorization: `Bearer ${token}` },
            })
                .then((r) => (r.ok ? r.json() : p))
                .catch(() => p)
        );
        const detailed = await Promise.all(detailRequests);

        displayPlaces(detailed);

    } catch (err) {
        const container = document.getElementById('places-list');
        if (container) {
            container.innerHTML = '<p class="empty-state">Failed to load places. Please check the API is running.</p>';
        }
    }
}

function displayPlaces(places) {
    const container = document.getElementById('places-list');
    if (!container) return;

    container.innerHTML = '';

    if (!places || places.length === 0) {
        container.innerHTML = '<p class="empty-state">No places available at the moment.</p>';
        return;
    }

    places.forEach((place, index) => {
        const div = document.createElement('div');
        div.className = 'place-card';
        div.dataset.price = place.price || 0;

        const price = place.price !== undefined ? `$${place.price}/night` : 'Price on request';
        const img = PLACE_IMAGES[index % PLACE_IMAGES.length];

        div.innerHTML = `
            <img src="${img}" alt="${escapeHtml(place.title)}" class="place-img">
            <h3>${escapeHtml(place.title)}</h3>
            <p class="price">${price}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        container.appendChild(div);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('places-list')) return;

    checkAuthentication();

    document.getElementById('price-filter').addEventListener('change', (event) => {
        const selected = event.target.value;
        document.querySelectorAll('.place-card').forEach((card) => {
            const price = parseFloat(card.dataset.price);
            card.style.display = (selected === 'all' || price <= parseFloat(selected))
                ? 'flex'
                : 'none';
        });
    });
});

/* =========================================
   TASK 3 — Place details page
   Fetch place by ID → display details + reviews
   Show "Write a Review" button only if authenticated
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('place-details')) return;

    const placeId = getQueryParam('id');
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    if (loginLink) {
        loginLink.style.display = token ? 'none' : 'block';
    }

    fetchPlaceDetails(placeId, token);
});

async function fetchPlaceDetails(placeId, token) {
    const detailsContainer = document.getElementById('place-details');
    const reviewsContainer = document.getElementById('reviews');

    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
        const response = await fetch(`${API_URL}/api/v1/places/${placeId}`, { headers });

        if (!response.ok) {
            detailsContainer.innerHTML = '<p class="empty-state">Place not found.</p>';
            return;
        }

        const place = await response.json();

        const amenitiesHtml = place.amenities && place.amenities.length > 0
            ? `<div class="amenities-list">${place.amenities.map((a) => {
                const icon = getAmenityIcon(a.name);
                const iconHtml = icon
                    ? `<img src="${icon}" alt="" class="amenity-icon">`
                    : '';
                return `<span class="amenity-tag">${iconHtml}${escapeHtml(a.name)}</span>`;
              }).join('')}</div>`
            : '<p>No amenities listed.</p>';

        const ownerName = place.owner
            ? `${escapeHtml(place.owner.first_name)} ${escapeHtml(place.owner.last_name)}`
            : 'Unknown';

        detailsContainer.innerHTML = `
            <div class="place-details">
                <h1>${escapeHtml(place.title)}</h1>
                <div class="place-info">
                    <p><strong>Host</strong>${ownerName}</p>
                    <p><strong>Price</strong>$${place.price}/night</p>
                    <p><strong>Location</strong>${place.latitude.toFixed(4)}, ${place.longitude.toFixed(4)}</p>
                </div>
                <p class="place-description">${escapeHtml(place.description || 'No description available.')}</p>
                <h3>Amenities</h3>
                ${amenitiesHtml}
                ${token ? `<a href="add_review.html?id=${placeId}" class="add-review-btn">Write a Review</a>` : ''}
            </div>
        `;

        await fetchReviews(placeId, reviewsContainer, headers);

    } catch (err) {
        detailsContainer.innerHTML = '<p class="empty-state">Failed to load place details.</p>';
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
            container.innerHTML = '<h2>Reviews</h2><p class="empty-state">Could not load reviews.</p>';
            return;
        }

        const reviews = await response.json();

        if (!reviews || reviews.length === 0) {
            container.innerHTML = '<h2>Reviews</h2><p class="empty-state">No reviews yet. Be the first!</p>';
            return;
        }

        const reviewsHtml = reviews.map((r) => `
            <div class="review-card">
                <p class="reviewer-name">${escapeHtml(r.user_id || 'Anonymous')}</p>
                ${renderStars(r.rating)}
                <p class="comment">${escapeHtml(r.comment)}</p>
            </div>
        `).join('');

        container.innerHTML = `<h2>Reviews (${reviews.length})</h2>${reviewsHtml}`;

    } catch (err) {
        container.innerHTML = '<h2>Reviews</h2><p class="empty-state">Failed to load reviews.</p>';
    }
}

/* =========================================
   TASK 4 — Add review page
   Only accessible to authenticated users
   POST review → redirect back to place
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    const reviewForm = document.getElementById('review-form');
    if (!reviewForm) return;

    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const placeId = getQueryParam('id');
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    // Update back link
    const backLink = document.getElementById('back-to-place');
    if (backLink) backLink.href = `place.html?id=${placeId}`;

    // Hide login link (user is authenticated)
    const loginLink = document.getElementById('login-link');
    if (loginLink) loginLink.style.display = 'none';

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        await submitReview(token, placeId);
    });
});

async function submitReview(token, placeId) {
    const messageEl = document.getElementById('review-message');
    const comment = document.getElementById('review-text').value.trim();
    const rating = parseInt(document.getElementById('rating').value, 10);

    if (!comment) {
        showMessage(messageEl, 'Please write your review.', 'error');
        return;
    }
    if (!rating || rating < 1 || rating > 5) {
        showMessage(messageEl, 'Please select a rating.', 'error');
        return;
    }

    // Decode user_id from JWT payload (base64url-encoded middle segment)
    let userId = null;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        userId = payload.sub;
    } catch {
        showMessage(messageEl, 'Session error. Please log in again.', 'error');
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
            showMessage(messageEl, 'Your review has been submitted!', 'success');
            document.getElementById('review-form').reset();
            setTimeout(() => {
                window.location.href = `place.html?id=${placeId}`;
            }, 1500);
        } else {
            const data = await response.json().catch(() => ({}));
            showMessage(messageEl, data.message || data.error || 'Failed to submit review.', 'error');
        }
    } catch (err) {
        showMessage(messageEl, 'Unable to reach the server. Please try again later.', 'error');
    }
}

/* =========================================
   UI helper — display message element
   ========================================= */

function showMessage(el, text, type) {
    if (!el) return;
    el.textContent = text;
    el.className = `message ${type}`;
}
