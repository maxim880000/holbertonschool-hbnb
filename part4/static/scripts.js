/*
  HBnB - Part 4
  Client-side scripts
*/

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);
        });
    }

    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        checkAuthentication();

        priceFilter.addEventListener('change', (event) => {
            const selected = event.target.value;
            const places = document.querySelectorAll('.place-card');
            places.forEach((card) => {
                if (selected === 'all') {
                    card.style.display = 'block';
                } else {
                    const price = parseFloat(card.dataset.price);
                    card.style.display = price <= parseFloat(selected) ? 'block' : 'none';
                }
            });
        });
    }

    /* ── Place details page ─────────────────────────────────────────── */
    const placeDetails = document.getElementById('place-details');
    if (placeDetails) {
        const placeId = getPlaceIdFromURL();
        if (placeId) {
            checkAuthenticationPlace(placeId);
        }
    }
});

/* ══ Helpers ════════════════════════════════════════════════════════════ */

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return null;
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

/* ══ Authentication ══════════════════════════════════════════════════════ */

/* Index page: show/hide login link + fetch places */
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

/* Place details page: show/hide add-review form + fetch place */
function checkAuthenticationPlace(placeId) {
    const token = getCookie('token');
    const addReviewSection = document.getElementById('add-review');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        if (addReviewSection) addReviewSection.style.display = 'none';
        if (loginLink) loginLink.style.display = 'block';
    } else {
        if (addReviewSection) addReviewSection.style.display = 'block';
        if (loginLink) loginLink.style.display = 'none';
    }

    fetchPlaceDetails(token, placeId);
}

/* ══ Login ══════════════════════════════════════════════════════════════ */

async function loginUser(email, password) {
    const response = await fetch(`${API_URL}/api/v1/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.href = 'index.html';
    } else {
        alert('Login failed: ' + response.statusText);
    }
}

/* ══ Places (index) ═════════════════════════════════════════════════════ */

async function fetchPlaces(token) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/places/`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const places = await response.json();
        displayPlaces(places);
    } else {
        console.error('Failed to fetch places:', response.statusText);
    }
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    places.forEach((place) => {
        const card = document.createElement('div');
        card.classList.add('place-card');
        card.dataset.price = place.price ?? 0;

        card.innerHTML = `
            <h2>${place.title}</h2>
            <p><strong>Price per night:</strong> $${place.price ?? 'N/A'}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

        placesList.appendChild(card);
    });
}

/* ══ Place details ══════════════════════════════════════════════════════ */

async function fetchPlaceDetails(token, placeId) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/places/${placeId}`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const place = await response.json();
        displayPlaceDetails(place);
        await fetchReviews(token, placeId);
    } else {
        console.error('Failed to fetch place details:', response.statusText);
    }
}

function displayPlaceDetails(place) {
    const placeInfo = document.querySelector('#place-details .place-info');
    placeInfo.innerHTML = '';

    const amenitiesList = place.amenities && place.amenities.length
        ? place.amenities.map(a => `<li>${a.name}</li>`).join('')
        : '<li>No amenities listed</li>';

    placeInfo.innerHTML = `
        <h1>${place.title}</h1>
        <p><strong>Host:</strong> ${place.owner.first_name} ${place.owner.last_name}</p>
        <p><strong>Price per night:</strong> $${place.price}</p>
        <p><strong>Description:</strong> ${place.description || 'No description available'}</p>
        <div class="amenities">
            <h3>Amenities</h3>
            <ul>${amenitiesList}</ul>
        </div>
    `;
}

async function fetchReviews(token, placeId) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/reviews/places/${placeId}/reviews`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const reviews = await response.json();
        displayReviews(reviews);
    } else {
        console.error('Failed to fetch reviews:', response.statusText);
    }
}

function displayReviews(reviews) {
    const reviewsSection = document.getElementById('reviews');
    const heading = reviewsSection.querySelector('h3');
    reviewsSection.innerHTML = '';
    if (heading) reviewsSection.appendChild(heading);

    if (!reviews.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No reviews yet.';
        reviewsSection.appendChild(empty);
        return;
    }

    reviews.forEach((review) => {
        const card = document.createElement('div');
        card.classList.add('review-card');
        card.innerHTML = `
            <p><strong>Rating:</strong> ${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</p>
            <p>${review.text}</p>
        `;
        reviewsSection.appendChild(card);
    });
}
