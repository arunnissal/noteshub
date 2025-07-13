// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Global state
let currentUser = null;
let accessToken = null;
let currentPage = 1;
let hasMoreNotes = true;
let searchTimeout = null;

// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const closeModal = document.getElementById('closeModal');
const closeRegisterModal = document.getElementById('closeRegisterModal');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const addNoteBtn = document.getElementById('addNoteBtn');
const addNoteModal = document.getElementById('addNoteModal');
const closeAddNoteModal = document.getElementById('closeAddNoteModal');
const addNoteForm = document.getElementById('addNoteForm');
const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');

// Navigation
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.section');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('accessToken');
    if (savedToken) {
        accessToken = savedToken;
        loadUserProfile();
        updateUIForLoggedInUser();
    }

    // Event listeners
    setupEventListeners();
    
    // Load initial data
    loadSubjects();
    loadNotes();
    
    // Initialize tooltips
    initializeTooltips();
}

function setupEventListeners() {
    // Login modal
    loginBtn.addEventListener('click', () => loginModal.style.display = 'block');
    closeModal.addEventListener('click', () => loginModal.style.display = 'none');
    closeRegisterModal.addEventListener('click', () => registerModal.style.display = 'none');
    
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) loginModal.style.display = 'none';
        if (e.target === registerModal) registerModal.style.display = 'none';
        if (e.target === addNoteModal) addNoteModal.style.display = 'none';
    });

    // Authentication
    document.getElementById('loginBtn').addEventListener('click', login);
    document.getElementById('registerBtn').addEventListener('click', register);
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.style.display = 'none';
        registerModal.style.display = 'block';
    });
    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        registerModal.style.display = 'none';
        loginModal.style.display = 'block';
    });

    // Add note
    addNoteBtn.addEventListener('click', () => addNoteModal.style.display = 'block');
    closeAddNoteModal.addEventListener('click', () => addNoteModal.style.display = 'none');
    document.getElementById('cancelAddNote').addEventListener('click', () => addNoteModal.style.display = 'none');
    addNoteForm.addEventListener('submit', addNote);

    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            showSection(targetId);
            
            // Close mobile menu
            navMenu.classList.remove('active');
        });
    });

    // Mobile navigation
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // Filters with debouncing
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterNotes();
        }, 300);
    });
    
    document.getElementById('subjectFilter').addEventListener('change', filterNotes);
    document.getElementById('semesterFilter').addEventListener('change', filterNotes);
    document.getElementById('priceFilter').addEventListener('change', filterNotes);

    // Load more
    document.getElementById('loadMoreBtn').addEventListener('click', loadMoreNotes);

    // Hero actions
    document.getElementById('getStartedBtn').addEventListener('click', () => {
        showSection('notes');
        if (!currentUser) {
            loginModal.style.display = 'block';
        }
    });

    document.getElementById('learnMoreBtn').addEventListener('click', () => {
        showSection('dashboard');
    });

    // Free note checkbox
    document.getElementById('noteFree').addEventListener('change', (e) => {
        const priceInput = document.getElementById('notePrice');
        if (e.target.checked) {
            priceInput.value = '0';
            priceInput.disabled = true;
        } else {
            priceInput.disabled = false;
        }
    });
}

// Navigation
function showSection(sectionId) {
    sections.forEach(section => section.classList.remove('active'));
    navLinks.forEach(link => link.classList.remove('active'));
    
    document.getElementById(sectionId).classList.add('active');
    document.querySelector(`[href="#${sectionId}"]`).classList.add('active');

    // Load section-specific data
    switch(sectionId) {
        case 'notes':
            loadNotes();
            break;
        case 'dashboard':
            loadDashboard();
            break;
        case 'wishlist':
            loadWishlist();
            break;
        case 'profile':
            loadUserProfile();
            break;
    }
}

// Authentication
async function login() {
    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;

    if (!phone || !password) {
        showNotification('Please enter both phone number and password', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.tokens.access;
            currentUser = data.user;
            
            // Save token
            localStorage.setItem('accessToken', accessToken);
            
            // Update UI
            updateUIForLoggedInUser();
            loginModal.style.display = 'none';
            
            // Clear form
            document.getElementById('phone').value = '';
            document.getElementById('password').value = '';
            
            // Load user profile
            await loadUserProfile();
            
            showNotification('Welcome back! Login successful.', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function register() {
    const phone = document.getElementById('regPhone').value;
    const name = document.getElementById('regName').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;

    if (!phone || !name || !password || !confirmPassword) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, name, password })
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.tokens.access;
            currentUser = data.user;
            
            // Save token
            localStorage.setItem('accessToken', accessToken);
            
            // Update UI
            updateUIForLoggedInUser();
            registerModal.style.display = 'none';
            
            // Clear form
            document.getElementById('regPhone').value = '';
            document.getElementById('regName').value = '';
            document.getElementById('regPassword').value = '';
            document.getElementById('regConfirmPassword').value = '';
            
            // Load user profile
            await loadUserProfile();
            
            showNotification('Account created successfully! Welcome to NotesHub.', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

function updateUIForLoggedInUser() {
    loginBtn.textContent = 'Dashboard';
    loginBtn.onclick = () => showSection('dashboard');
    
    // Show user-specific sections
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.textContent === 'Wishlist' || link.textContent === 'Profile') {
            link.style.display = 'block';
        }
    });
}

function logout() {
    localStorage.removeItem('accessToken');
    accessToken = null;
    currentUser = null;
    
    loginBtn.textContent = 'Sign In';
    loginBtn.onclick = () => loginModal.style.display = 'block';
    
    showNotification('Logged out successfully', 'success');
    
    // Reset UI
    location.reload();
}

// API Helper
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`;
    }

    try {
        const response = await fetch(url, config);
        
        if (response.status === 401) {
            // Token expired
            localStorage.removeItem('accessToken');
            accessToken = null;
            currentUser = null;
            showNotification('Session expired. Please login again.', 'warning');
            return null;
        }
        
        return response;
    } catch (error) {
        showNotification('Network error. Please check your connection.', 'error');
        return null;
    }
}

// Data Loading Functions
async function loadSubjects() {
    try {
        const response = await apiRequest('/subjects/');
        if (response && response.ok) {
            const subjects = await response.json();
            populateSubjectFilters(subjects);
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

function populateSubjectFilters(subjects) {
    const subjectFilter = document.getElementById('subjectFilter');
    const noteSubject = document.getElementById('noteSubject');
    
    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.id;
        option.textContent = `${subject.code} - ${subject.name}`;
        
        subjectFilter.appendChild(option.cloneNode(true));
        noteSubject.appendChild(option);
    });
}

async function loadNotes(page = 1) {
    try {
        const response = await apiRequest(`/notes/?page=${page}`);
        if (response && response.ok) {
            const data = await response.json();
            const notes = data.results || data;
            
            if (page === 1) {
                displayNotes(notes);
            } else {
                appendNotes(notes);
            }
            
            hasMoreNotes = data.next ? true : false;
            document.getElementById('loadMoreBtn').style.display = hasMoreNotes ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error loading notes:', error);
        showNotification('Error loading notes', 'error');
    }
}

function displayNotes(notes) {
    const notesGrid = document.getElementById('notesGrid');
    
    if (notes.length === 0) {
        notesGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No notes found</h3>
                <p>Try adjusting your search criteria or be the first to add a note!</p>
                <button class="btn btn-primary" onclick="addNoteModal.style.display = 'block'">
                    <i class="fas fa-plus"></i> Add First Note
                </button>
            </div>
        `;
        return;
    }
    
    notesGrid.innerHTML = notes.map(note => createNoteCard(note)).join('');
}

function appendNotes(notes) {
    const notesGrid = document.getElementById('notesGrid');
    const noteCards = notes.map(note => createNoteCard(note)).join('');
    notesGrid.insertAdjacentHTML('beforeend', noteCards);
}

function createNoteCard(note) {
    const isInWishlist = note.in_wishlist || false;
    const priceDisplay = note.is_free ? 'Free' : `₹${note.price}`;
    const priceClass = note.is_free ? 'free' : '';
    
    return `
        <div class="note-card" data-note-id="${note.id}">
            <div class="note-header">
                <h3 class="note-title">${note.title}</h3>
                <span class="note-price ${priceClass}">${priceDisplay}</span>
            </div>
            <div class="note-subject">${note.subject_name}</div>
            <p class="note-description">${note.description}</p>
            <div class="note-meta">
                <span><i class="fas fa-calendar"></i> ${note.semester}${getOrdinalSuffix(note.semester)} Semester</span>
                <span><i class="fas fa-eye"></i> ${note.views} views</span>
            </div>
            <div class="note-actions">
                <button class="btn btn-outline btn-sm" onclick="contactSeller('${note.contact_info}')">
                    <i class="fas fa-phone"></i> Contact Seller
                </button>
                <button class="btn ${isInWishlist ? 'btn-danger' : 'btn-success'} btn-sm" 
                        onclick="${isInWishlist ? 'removeFromWishlist' : 'addToWishlist'}('${note.id}')">
                    <i class="fas fa-${isInWishlist ? 'trash' : 'heart'}"></i> 
                    ${isInWishlist ? 'Remove' : 'Add to Wishlist'}
                </button>
            </div>
        </div>
    `;
}

function getOrdinalSuffix(num) {
    const j = num % 10;
    const k = num % 100;
    if (j == 1 && k != 11) return "st";
    if (j == 2 && k != 12) return "nd";
    if (j == 3 && k != 13) return "rd";
    return "th";
}

async function loadMoreNotes() {
    currentPage++;
    await loadNotes(currentPage);
}

async function addNote(e) {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('noteTitle').value,
        subject: document.getElementById('noteSubject').value,
        description: document.getElementById('noteDescription').value,
        semester: document.getElementById('noteSemester').value,
        year: document.getElementById('noteYear').value,
        price: document.getElementById('notePrice').value,
        contact_info: document.getElementById('noteContact').value,
        tags: document.getElementById('noteTags').value,
        is_free: document.getElementById('noteFree').checked
    };

    try {
        const response = await apiRequest('/notes/', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        if (response && response.ok) {
            showNotification('Note added successfully!', 'success');
            addNoteModal.style.display = 'none';
            addNoteForm.reset();
            document.getElementById('notePrice').disabled = false;
            
            // Reload notes
            currentPage = 1;
            loadNotes();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to add note', 'error');
        }
    } catch (error) {
        showNotification('Error adding note', 'error');
    }
}

async function addToWishlist(noteId) {
    try {
        const response = await apiRequest('/wishlist/', {
            method: 'POST',
            body: JSON.stringify({ note_id: noteId })
        });

        if (response && response.ok) {
            showNotification('Added to wishlist!', 'success');
            // Update button state
            const button = document.querySelector(`[data-note-id="${noteId}"] .btn-success`);
            if (button) {
                button.className = 'btn btn-danger btn-sm';
                button.innerHTML = '<i class="fas fa-trash"></i> Remove';
                button.onclick = () => removeFromWishlist(noteId);
            }
        } else {
            showNotification('Failed to add to wishlist', 'error');
        }
    } catch (error) {
        showNotification('Error adding to wishlist', 'error');
    }
}

async function loadWishlist() {
    try {
        const response = await apiRequest('/wishlist/');
        if (response && response.ok) {
            const wishlist = await response.json();
            displayWishlist(wishlist);
        }
    } catch (error) {
        console.error('Error loading wishlist:', error);
    }
}

function displayWishlist(wishlist) {
    const wishlistGrid = document.getElementById('wishlistGrid');
    
    if (wishlist.length === 0) {
        wishlistGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-heart"></i>
                <h3>Your wishlist is empty</h3>
                <p>Start browsing notes and add them to your wishlist for easy access!</p>
                <button class="btn btn-primary" onclick="showSection('notes')">
                    <i class="fas fa-search"></i> Browse Notes
                </button>
            </div>
        `;
        return;
    }
    
    wishlistGrid.innerHTML = wishlist.map(item => createWishlistCard(item)).join('');
}

function createWishlistCard(item) {
    const note = item.note;
    const priceDisplay = note.is_free ? 'Free' : `₹${note.price}`;
    const priceClass = note.is_free ? 'free' : '';
    
    return `
        <div class="note-card">
            <div class="note-header">
                <h3 class="note-title">${note.title}</h3>
                <span class="note-price ${priceClass}">${priceDisplay}</span>
            </div>
            <div class="note-subject">${note.subject_name}</div>
            <p class="note-description">${note.description}</p>
            <div class="note-meta">
                <span><i class="fas fa-calendar"></i> ${note.semester}${getOrdinalSuffix(note.semester)} Semester</span>
                <span><i class="fas fa-clock"></i> Added ${formatDate(item.created_at)}</span>
            </div>
            <div class="note-actions">
                <button class="btn btn-outline btn-sm" onclick="contactSeller('${note.contact_info}')">
                    <i class="fas fa-phone"></i> Contact Seller
                </button>
                <button class="btn btn-danger btn-sm" onclick="removeFromWishlist('${item.id}')">
                    <i class="fas fa-trash"></i> Remove
                </button>
            </div>
        </div>
    `;
}

async function removeFromWishlist(wishlistId) {
    try {
        const response = await apiRequest(`/wishlist/${wishlistId}/`, {
            method: 'DELETE'
        });

        if (response && response.ok) {
            showNotification('Removed from wishlist', 'success');
            // Reload wishlist
            loadWishlist();
        } else {
            showNotification('Failed to remove from wishlist', 'error');
        }
    } catch (error) {
        showNotification('Error removing from wishlist', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await apiRequest('/profile/');
        if (response && response.ok) {
            const profile = await response.json();
            displayProfile(profile);
        } else if (response && response.status === 404) {
            showCreateProfileForm();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function displayProfile(profile) {
    const profileContent = document.getElementById('profileContent');
    
    profileContent.innerHTML = `
        <div class="profile-header">
            <div class="profile-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
            <div class="profile-info">
                <h3>${profile.user_name || 'User'}</h3>
                <p class="profile-phone">${profile.phone}</p>
            </div>
        </div>
        
        <div class="profile-details">
            <div class="detail-group">
                <label>Student ID</label>
                <p>${profile.student_id}</p>
            </div>
            <div class="detail-group">
                <label>College</label>
                <p>${profile.college}</p>
            </div>
            <div class="detail-group">
                <label>Department</label>
                <p>${profile.department}</p>
            </div>
            <div class="detail-group">
                <label>Year</label>
                <p>${profile.year}${getOrdinalSuffix(profile.year)} Year</p>
            </div>
            <div class="detail-group">
                <label>Rating</label>
                <p><i class="fas fa-star"></i> ${profile.rating || '0.00'}</p>
            </div>
        </div>
        
        <div class="profile-actions">
            <button class="btn btn-outline" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        </div>
    `;
}

function showCreateProfileForm() {
    const profileContent = document.getElementById('profileContent');
    
    profileContent.innerHTML = `
        <div class="profile-form">
            <h3>Complete Your Profile</h3>
            <p>Please provide your student information to get started.</p>
            
            <form id="createProfileForm">
                <div class="form-group">
                    <label for="studentId">Student ID *</label>
                    <div class="input-group">
                        <i class="fas fa-id-card"></i>
                        <input type="text" id="studentId" required placeholder="Enter your student ID">
                    </div>
                </div>
                <div class="form-group">
                    <label for="college">College *</label>
                    <div class="input-group">
                        <i class="fas fa-university"></i>
                        <input type="text" id="college" required placeholder="Enter your college name">
                    </div>
                </div>
                <div class="form-group">
                    <label for="department">Department *</label>
                    <div class="input-group">
                        <i class="fas fa-graduation-cap"></i>
                        <input type="text" id="department" required placeholder="Enter your department">
                    </div>
                </div>
                <div class="form-group">
                    <label for="year">Year *</label>
                    <div class="input-group">
                        <i class="fas fa-calendar"></i>
                        <select id="year" required>
                            <option value="">Select Year</option>
                            <option value="1">1st Year</option>
                            <option value="2">2nd Year</option>
                            <option value="3">3rd Year</option>
                            <option value="4">4th Year</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="bio">Bio</label>
                    <div class="input-group">
                        <i class="fas fa-user"></i>
                        <textarea id="bio" placeholder="Tell us about yourself..."></textarea>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save Profile
                </button>
            </form>
        </div>
    `;
    
    document.getElementById('createProfileForm').addEventListener('submit', createProfile);
}

async function createProfile(e) {
    e.preventDefault();
    
    const formData = {
        student_id: document.getElementById('studentId').value,
        college: document.getElementById('college').value,
        department: document.getElementById('department').value,
        year: document.getElementById('year').value,
        bio: document.getElementById('bio').value
    };

    try {
        const response = await apiRequest('/profile/', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        if (response && response.ok) {
            showNotification('Profile created successfully!', 'success');
            loadUserProfile();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to create profile', 'error');
        }
    } catch (error) {
        showNotification('Error creating profile', 'error');
    }
}

async function loadDashboard() {
    if (!currentUser) {
        showNotification('Please login to view dashboard', 'warning');
        return;
    }
    
    try {
        // Load dashboard stats
        const statsResponse = await apiRequest('/dashboard/stats/');
        if (statsResponse && statsResponse.ok) {
            const stats = await statsResponse.json();
            displayDashboardStats(stats);
        }
        
        // Load recent activity
        const activityResponse = await apiRequest('/dashboard/activity/');
        if (activityResponse && activityResponse.ok) {
            const activity = await activityResponse.json();
            displayActivity(activity);
        }
        
        // Load top notes
        const topNotesResponse = await apiRequest('/dashboard/top-notes/');
        if (topNotesResponse && topNotesResponse.ok) {
            const topNotes = await topNotesResponse.json();
            displayTopNotes(topNotes);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayDashboardStats(stats) {
    const dashboardStats = document.getElementById('dashboardStats');
    
    dashboardStats.innerHTML = `
        <div class="stat-card">
            <h3>${stats.total_notes || 0}</h3>
            <p>Notes Created</p>
        </div>
        <div class="stat-card">
            <h3>${stats.total_sales || 0}</h3>
            <p>Total Sales</p>
        </div>
        <div class="stat-card">
            <h3>${stats.wishlist_count || 0}</h3>
            <p>Wishlist Items</p>
        </div>
        <div class="stat-card">
            <h3>${stats.rating || '0.00'}</h3>
            <p>Average Rating</p>
        </div>
    `;
}

function displayActivity(activity) {
    const activityList = document.getElementById('activityList');
    
    if (activity.length === 0) {
        activityList.innerHTML = '<p class="empty-state">No recent activity</p>';
        return;
    }
    
    activityList.innerHTML = activity.map(item => `
        <div class="activity-item">
            <div class="activity-icon">
                <i class="fas fa-${getActivityIcon(item.type)}"></i>
            </div>
            <div class="activity-content">
                <h4>${item.title}</h4>
                <p>${formatDate(item.created_at)}</p>
            </div>
        </div>
    `).join('');
}

function displayTopNotes(notes) {
    const topNotesList = document.getElementById('topNotesList');
    
    if (notes.length === 0) {
        topNotesList.innerHTML = '<p class="empty-state">No top notes yet</p>';
        return;
    }
    
    topNotesList.innerHTML = notes.map(note => `
        <div class="top-note-item">
            <div class="note-info">
                <h4>${note.title}</h4>
                <p><i class="fas fa-star"></i> ${note.rating} • ${note.views} views</p>
            </div>
            <button class="btn btn-sm btn-outline" onclick="contactSeller('${note.contact_info}')">
                Contact
            </button>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'note_created': 'plus',
        'note_sold': 'check',
        'wishlist_added': 'heart',
        'review_received': 'star'
    };
    return icons[type] || 'circle';
}

function filterNotes() {
    const searchTerm = document.getElementById('searchInput').value;
    const subject = document.getElementById('subjectFilter').value;
    const semester = document.getElementById('semesterFilter').value;
    const priceRange = document.getElementById('priceFilter').value;
    
    // Reset pagination
    currentPage = 1;
    
    // Build query string
    const params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    if (subject) params.append('subject', subject);
    if (semester) params.append('semester', semester);
    if (priceRange) params.append('price_range', priceRange);
    
    // Load filtered notes
    loadFilteredNotes(params.toString());
}

async function loadFilteredNotes(queryString) {
    try {
        const response = await apiRequest(`/notes/?${queryString}`);
        if (response && response.ok) {
            const data = await response.json();
            const notes = data.results || data;
            displayNotes(notes);
        }
    } catch (error) {
        console.error('Error filtering notes:', error);
    }
}

function contactSeller(contactInfo) {
    if (contactInfo) {
        // Create a temporary input to copy contact info
        const tempInput = document.createElement('input');
        tempInput.value = contactInfo;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        
        showNotification('Contact information copied to clipboard!', 'success');
    } else {
        showNotification('Contact information not available', 'warning');
    }
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays < 7) return `${diffDays - 1} days ago`;
    
    return date.toLocaleDateString();
}

function showNotification(message, type = 'success') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 5000);
}

function initializeTooltips() {
    // Add tooltip functionality to elements with data-tooltip attribute
    document.addEventListener('mouseover', (e) => {
        if (e.target.hasAttribute('data-tooltip')) {
            // Tooltip functionality is handled by CSS
        }
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        loginModal.style.display = 'none';
        registerModal.style.display = 'none';
        addNoteModal.style.display = 'none';
    }
});

// Service Worker for PWA features (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                // Service Worker registered successfully
            })
            .catch(registrationError => {
                // Service Worker registration failed
            });
    });
} 