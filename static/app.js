const DB = {
    loadUsers() {
        return JSON.parse(localStorage.getItem('ln_users') || '[]');
    },
    saveUsers(users) {
        localStorage.setItem('ln_users', JSON.stringify(users));
    },
    loadNews() {
        return JSON.parse(localStorage.getItem('ln_news') || '[]');
    },
    saveNews(news) {
        localStorage.setItem('ln_news', JSON.stringify(news));
    },
    currentUser() {
        const email = localStorage.getItem('ln_session');
        if (!email) return null;
        return this.loadUsers().find(u => u.email === email) || null;
    },
    login(email) {
        localStorage.setItem('ln_session', email);
    },
    logout() {
        localStorage.removeItem('ln_session');
    }
};

(function seed() {
    const users = DB.loadUsers();
    if (!users.some(u => u.email === 'admin@news.ge')) {
        users.push({ username: 'Admin', email: 'admin@news.ge', password: 'AdminPassword123', isAdmin: true });
        DB.saveUsers(users);
    }
})();

function flash(message, category) {
    const queue = JSON.parse(sessionStorage.getItem('ln_flash') || '[]');
    queue.push({ message, category });
    sessionStorage.setItem('ln_flash', JSON.stringify(queue));
}

function renderFlashes() {
    const holder = document.getElementById('flash-container');
    if (!holder) return;
    const queue = JSON.parse(sessionStorage.getItem('ln_flash') || '[]');
    sessionStorage.removeItem('ln_flash');
    holder.innerHTML = queue.map(f => `
        <div class="alert alert-${f.category} alert-dismissible fade show" role="alert">
            ${escapeHtml(f.message)}
            <button type="button" class="close" data-dismiss="alert">&times;</button>
        </div>`).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(iso, withTime) {
    const d = new Date(iso);
    const pad = n => String(n).padStart(2, '0');
    let s = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    if (withTime) s += ` ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    return s;
}

function renderNavbar() {
    const holder = document.getElementById('navbar-holder');
    if (!holder) return;
    const user = DB.currentUser();

    let leftLinks = `
        <li class="nav-item"><a class="nav-link" href="index.html">მთავარი</a></li>`;
    let rightLinks = '';

    if (user) {
        leftLinks += `
        <li class="nav-item"><a class="nav-link" href="add_news.html">➕ სიახლის დამატება</a></li>`;
        if (user.isAdmin) {
            leftLinks += `
        <li class="nav-item"><a class="nav-link text-warning" href="admin.html">🛠️ ადმინ პანელი</a></li>`;
        }
        rightLinks = `
        <li class="nav-item"><span class="nav-link text-white mr-2">👤 ${escapeHtml(user.username)}</span></li>
        <li class="nav-item"><a class="btn btn-outline-light btn-sm" href="#" id="logout-link">გამოსვლა</a></li>`;
    } else {
        rightLinks = `
        <li class="nav-item"><a class="nav-link" href="login.html">შესვლა</a></li>
        <li class="nav-item"><a class="btn btn-primary btn-sm ml-2" href="register.html">რეგისტრაცია</a></li>`;
    }

    holder.innerHTML = `
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand font-weight-bold" href="index.html">🏡 ადგილობრივი ამბები</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav mr-auto">${leftLinks}</ul>
                <ul class="navbar-nav ml-auto align-items-center">
                    ${rightLinks}
                    <li class="nav-item ml-3">
                        <a href="https://www.tbcbank.ge/web/ka/web/guest/education" target="_blank">
                            <img src="static/images/tbc_logo.png" alt="TBC Education" style="height: 35px; border-radius: 5px;">
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>`;

    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', e => {
            e.preventDefault();
            DB.logout();
            flash('თქვენ გამოხვედით სისტემიდან.', 'info');
            window.location.href = 'index.html';
        });
    }
}

function requireLogin() {
    if (!DB.currentUser()) {
        flash('ამ გვერდის სანახავად გაიარეთ ავტორიზაცია.', 'info');
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function requireAdmin() {
    if (!requireLogin()) return false;
    if (!DB.currentUser().isAdmin) {
        flash('ამ გვერდზე წვდომა მხოლოდ ადმინისტრატორს აქვს!', 'danger');
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

function deleteNews(id) {
    if (!confirm('ნამდვილად გსურთ ამ სიახლის წაშლა?')) return;
    DB.saveNews(DB.loadNews().filter(n => n.id !== id));
    flash('სიახლე წარმატებით წაიშალა!', 'success');
    window.location.reload();
}

document.addEventListener('DOMContentLoaded', () => {
    renderNavbar();
    renderFlashes();
});
