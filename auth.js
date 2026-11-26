/**
 * LifeGraph AI – Frontend Authentication Controller (auth.js)
 * Manages:
 * - Session verification against GET /auth/me
 * - User profile display in the top header
 * - User logout action via POST /auth/logout
 * - Redirects for protected views
 */

(() => {
  'use strict';

  const LifeGraphAuth = {
    currentUser: null,

    getApiBaseUrl() {
      // 1. Check window-level override
      if (window.LIFEGRAPH_API_BASE) {
        return window.LIFEGRAPH_API_BASE.replace(/\/+$/, '');
      }
      // 2. Check if LifeGraphConfig from script.js is loaded
      if (window.LifeGraphConfig && window.LifeGraphConfig.apiBaseUrl) {
        try {
          const parsed = new URL(window.LifeGraphConfig.apiBaseUrl);
          return `${parsed.protocol}//${parsed.host}`;
        } catch (e) {}
      }
      // 3. If running on backend port directly (8000), use current origin
      if (window.location.port === '8000') {
        return window.location.origin;
      }
      // 4. If running from frontend dev server (e.g. Live Server on 5500, 3000) or file://
      // target backend at the same hostname on port 8000
      const hostname = window.location.hostname && window.location.hostname !== ''
        ? window.location.hostname
        : '127.0.0.1';
      return `http://${hostname}:8000`;
    },

    async init() {
      await this.checkAuthStatus();
      this.bindProfileDropdown();
    },

    async checkAuthStatus() {
      try {
        const baseUrl = this.getApiBaseUrl();
        const response = await fetch(`${baseUrl}/auth/me`, {
          method: 'GET',
          credentials: 'include',
          headers: this.getAuthHeaders(),
        });

        if (response.ok) {
          this.currentUser = await response.json();
          this.renderAuthenticatedUser(this.currentUser);
        } else {
          // Unauthenticated or expired session (HTTP 401/403)
          if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('lifegraph_token');
            localStorage.removeItem('lifegraph_user');
          }
          this.currentUser = null;
          this.renderUnauthenticatedState();
        }
      } catch (err) {
        console.warn('[LifeGraph Auth] Could not reach auth status endpoint:', err);
        // Only if network error/offline, fallback to cached state if available
        const cachedUser = localStorage.getItem('lifegraph_user');
        if (cachedUser) {
          try {
            this.currentUser = JSON.parse(cachedUser);
            this.renderAuthenticatedUser(this.currentUser);
            return;
          } catch (e) {}
        }
        this.renderUnauthenticatedState();
      }
    },

    getAuthHeaders() {
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('lifegraph_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      return headers;
    },

    renderAuthenticatedUser(user) {
      const userNameEl = document.getElementById('user-name');
      const userRoleEl = document.getElementById('user-role');
      const avatarEl = document.getElementById('user-avatar');

      if (userNameEl) {
        userNameEl.textContent = user.full_name || 'Authenticated User';
      }
      if (userRoleEl) {
        userRoleEl.textContent = user.email || 'Member';
      }
      if (avatarEl) {
        avatarEl.innerHTML = '<i class="fa-solid fa-user-check" style="color: var(--color-primary-cyan, #22D3EE);"></i>';
      }

      this.createProfileDropdown(true, user);
    },

    renderUnauthenticatedState() {
      const userNameEl = document.getElementById('user-name');
      const userRoleEl = document.getElementById('user-role');
      const avatarEl = document.getElementById('user-avatar');

      if (userNameEl) {
        userNameEl.textContent = 'Guest Explorer';
      }
      if (userRoleEl) {
        userRoleEl.innerHTML = '<a href="login.html" style="color:var(--color-primary-cyan, #22D3EE); text-decoration:none; font-weight:600;">Sign In / Register</a>';
      }
      if (avatarEl) {
        avatarEl.innerHTML = '<i class="fa-solid fa-user-lock"></i>';
      }

      this.createProfileDropdown(false);
    },

    createProfileDropdown(isAuthenticated, user = null) {
      const profileSection = document.getElementById('user-profile-section');
      if (!profileSection) return;

      // Remove existing dropdown if any
      const existingDropdown = document.getElementById('auth-profile-dropdown');
      if (existingDropdown) existingDropdown.remove();

      const dropdown = document.createElement('div');
      dropdown.id = 'auth-profile-dropdown';
      dropdown.className = 'auth-dropdown-menu';

      Object.assign(dropdown.style, {
        position: 'absolute',
        top: '100%',
        right: '0',
        marginTop: '8px',
        width: '240px',
        background: 'var(--bg-panel, #111C2D)',
        border: '1px solid var(--border-color, #26364B)',
        borderRadius: '8px',
        boxShadow: '0 12px 32px rgba(0, 0, 0, 0.65)',
        padding: '12px',
        display: 'none',
        zIndex: '1000',
        backdropFilter: 'blur(10px)',
      });

      if (isAuthenticated && user) {
        dropdown.innerHTML = `
          <div style="padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px solid var(--border-color, #26364B);">
            <div style="font-size: 0.88rem; font-weight: 600; color: #FFFFFF;">${user.full_name}</div>
            <div style="font-size: 0.76rem; color: var(--text-secondary, #94A3B8); word-break: break-all;">${user.email}</div>
            <div style="font-size: 0.70rem; color: var(--color-success, #22C55E); margin-top: 4px;">
              <i class="fa-solid fa-circle" style="font-size: 0.5rem;"></i> Active Session
            </div>
          </div>
          <button type="button" id="btn-user-logout" style="width:100%; display:flex; align-items:center; gap:8px; background:rgba(239, 68, 68, 0.12); color:#FCA5A5; border:1px solid rgba(239, 68, 68, 0.25); border-radius:6px; padding:9px 12px; font-size:0.82rem; font-weight:500; cursor:pointer; transition:all 0.2s ease;">
            <i class="fa-solid fa-right-from-bracket"></i>
            <span>Log Out</span>
          </button>
        `;
      } else {
        dropdown.innerHTML = `
          <div style="padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px solid var(--border-color, #26364B);">
            <div style="font-size: 0.84rem; font-weight: 600; color: #FFFFFF;">Access Restricted</div>
            <div style="font-size: 0.75rem; color: var(--text-secondary, #94A3B8);">Sign in to access private graph workflows</div>
          </div>
          <a href="login.html" style="display:block; text-align:center; background:linear-gradient(135deg, var(--color-primary-cyan, #22D3EE), var(--color-secondary-blue, #3B82F6)); color:#080D18; border-radius:6px; padding:9px 12px; font-size:0.82rem; font-weight:600; text-decoration:none; margin-bottom:8px;">
            Log In
          </a>
          <a href="signup.html" style="display:block; text-align:center; background:var(--bg-input, #0A111E); color:var(--text-primary, #E5EDF7); border:1px solid var(--border-color, #26364B); border-radius:6px; padding:8px 12px; font-size:0.80rem; font-weight:500; text-decoration:none;">
            Create Account
          </a>
        `;
      }

      profileSection.style.position = 'relative';
      profileSection.appendChild(dropdown);

      // Bind logout button if present
      const btnLogout = dropdown.querySelector('#btn-user-logout');
      if (btnLogout) {
        btnLogout.addEventListener('click', (e) => {
          e.stopPropagation();
          this.logout();
        });
      }
    },

    bindProfileDropdown() {
      const profileButton = document.getElementById('user-profile-button');
      if (!profileButton) return;

      profileButton.addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = document.getElementById('auth-profile-dropdown');
        if (!dropdown) return;

        const isOpen = dropdown.style.display === 'block';
        dropdown.style.display = isOpen ? 'none' : 'block';
        profileButton.setAttribute('aria-expanded', String(!isOpen));
      });

      // Close on outside click
      document.addEventListener('click', () => {
        const dropdown = document.getElementById('auth-profile-dropdown');
        if (dropdown) {
          dropdown.style.display = 'none';
          const profileButton = document.getElementById('user-profile-button');
          if (profileButton) profileButton.setAttribute('aria-expanded', 'false');
        }
      });
    },

    async logout() {
      try {
        const baseUrl = this.getApiBaseUrl();
        await fetch(`${baseUrl}/auth/logout`, {
          method: 'POST',
          credentials: 'include',
        });
      } catch (err) {
        console.warn('[LifeGraph Auth] Logout request error:', err);
      } finally {
        localStorage.removeItem('lifegraph_token');
        localStorage.removeItem('lifegraph_user');
        window.location.href = 'login.html';
      }
    }
  };

  window.LifeGraphAuth = LifeGraphAuth;

  document.addEventListener('DOMContentLoaded', () => {
    LifeGraphAuth.init();
  });
})();
