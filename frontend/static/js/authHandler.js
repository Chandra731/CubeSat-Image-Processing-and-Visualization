import { BASE_URL } from './apiHandler.js';

function showToast(message, isSuccess = true) {
    const toast = document.createElement('div');
    toast.className = `toast ${isSuccess ? 'success' : 'error'}`;
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function validateEmail(email) {
    // Improved stricter email regex pattern
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(email);
}

export async function login(email, password) {
    if (!email || !password) {
        showToast('Please fill in all fields', false);
        return false;
    }
    if (!validateEmail(email) && email.indexOf('@') !== -1) {
        showToast('Please enter a valid email address', false);
        return false;
    }
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username: email, password }),
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, true);
            return true;
        } else {
            showToast(data.message, false);
            return false;
        }
    } catch (error) {
        showToast('Login failed. Please try again.', false);
        return false;
    }
}

export async function register(username, email, password, confirmPassword) {
    // Client-side validation
    if (!username || !email || !password || !confirmPassword) {
        showToast('Please fill in all fields', false);
        return false;
    }
    if (username.length < 3 || username.length > 30) {
        showToast('Username must be between 3 and 30 characters', false);
        return false;
    }
    const usernameRegex = /^[a-zA-Z0-9_.-]+$/;
    if (!usernameRegex.test(username)) {
        showToast('Username can only contain letters, numbers, underscores, dots, and hyphens', false);
        return false;
    }
    if (!validateEmail(email)) {
        showToast('Please enter a valid email address', false);
        return false;
    }
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', false);
        return false;
    }
    if (password !== confirmPassword) {
        showToast('Passwords do not match', false);
        return false;
    }
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password, confirmPassword }),
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, true);
            return true;
        } else {
            showToast(data.message, false);
            return false;
        }
    } catch (error) {
        showToast('Registration failed. Please try again.', false);
        return false;
    }
}


export async function requestPasswordReset(email) {
    if (!email) {
        showToast('Please enter your email', false);
        return false;
    }
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/password_reset_request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email }),
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, true);
            return true;
        } else {
            showToast(data.message, false);
            return false;
        }
    } catch (error) {
        showToast('Password reset request failed. Please try again.', false);
        return false;
    }
}

export async function resetPassword(token, password, confirmPassword) {
    if (!password || !confirmPassword) {
        showToast('Please fill in all fields', false);
        return false;
    }
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', false);
        return false;
    }
    if (password !== confirmPassword) {
        showToast('Passwords do not match', false);
        return false;
    }
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/password_reset/${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password, confirmPassword }),
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, true);
            return true;
        } else {
            showToast(data.message, false);
            return false;
        }
    } catch (error) {
        showToast('Password reset failed. Please try again.', false);
        return false;
    }
}

export async function logout() {
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/logout`, {
            method: 'POST',
            credentials: 'include',
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, true);
            return true;
        } else {
            showToast('Logout failed.', false);
            return false;
        }
    } catch (error) {
        showToast('Logout failed. Please try again.', false);
        return false;
    }
}

export async function checkLoginStatus() {
    try {
        const response = await fetch(`${BASE_URL.replace('/api', '')}/auth/status`, {
            method: 'GET',
            credentials: 'include',
        });
        const data = await response.json();
        return data.success === true;
    } catch (error) {
        return false;
    }
}

