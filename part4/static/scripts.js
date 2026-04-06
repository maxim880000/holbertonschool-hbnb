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
});

/* ── Authentication ─────────────────────────────────────────────────── */

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return null;
}

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

/* ── Login ──────────────────────────────────────────────────────────── */

async function loginUser(email, password) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/users/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
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

/* ── Places ─────────────────────────────────────────────────────────── */

async function fetchPlaces(token) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
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
        card.dataset.price = place.price;

        card.innerHTML = `
            <h2>${place.title}</h2>
            <p>${place.description || ''}</p>
            <p><strong>Price per night:</strong> $${place.price}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

        placesList.appendChild(card);
    });
}
