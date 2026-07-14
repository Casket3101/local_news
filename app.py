from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, News
from forms import RegistrationForm, LoginForm, NewsForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'tbc_techschool_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'ამ გვერდის სანახავად გაიარეთ ავტორიზაცია.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    approved_news = News.query.filter_by(is_approved=True).order_by(News.date_posted.desc()).all()
    return render_template('index.html', news_list=approved_news)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_exists = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
        if user_exists:
            flash('მომხმარებელი ამ სახელით ან ელ-ფოსტით უკვე არსებობს!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('რეგისტრაცია წარმატებით გაიარეთ! შეგიძლიათ შეხვიდეთ.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash(f'მოგესალმებით, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('არასწორი ელ-ფოსტა ან პაროლი!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('თქვენ გამოხვედით სისტემიდან.', 'info')
    return redirect(url_for('index'))

@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        new_post = News(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        flash('თქვენი სიახლე გაიგზავნა! ის გამოჩნდება მას შემდეგ, რაც ადმინისტრატორი დაამტკიცებს.', 'warning')
        return redirect(url_for('index'))
    return render_template('add_news.html', form=form)

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('ამ გვერდზე წვდომა მხოლოდ ადმინისტრატორს აქვს!', 'danger')
        return redirect(url_for('index'))
    pending_news = News.query.filter_by(is_approved=False).all()
    return render_template('admin.html', news_list=pending_news)

@app.route('/admin/approve/<int:news_id>')
@login_required
def approve_news(news_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    post = News.query.get_or_404(news_id)
    post.is_approved = True
    db.session.commit()
    flash('სიახლე წარმატებით დამტკიცდა და გამოქვეყნდა!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/news/delete/<int:news_id>', methods=['POST'])
@login_required
def delete_news(news_id):
    post = News.query.get_or_404(news_id)
    db.session.delete(post)
    db.session.commit()
    flash('სიახლე წარმატებით წაიშალა!', 'success')
    return redirect(request.referrer or url_for('index'))


with app.app_context():
    db.create_all()
    admin_exists = User.query.filter_by(email="admin@news.ge").first()
    if not admin_exists:
        admin_user = User(username="Admin", email="admin@news.ge", password="AdminPassword123", is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)