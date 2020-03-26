from blog.models import User, Post, likes
from flask import  request, render_template, url_for, flash, redirect, abort
from blog.forms import Registration, Login, PostForm
from blog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.all()
    return render_template ('home.html', posts=posts)


@app.route('/post_list')
def post_list():
    all_posts = Post.query.all()
    return render_template('post_list.html', posts=all_posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Registration()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account was created. You can log in','success')
        return redirect (url_for('index'))
    return render_template('register.html', title = 'Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Login()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user and bcrypt.check_password_hash(user.password, form.password.data):
           login_user(user,remember=form.remember.data)
           next_page = request.args.get('next')
           return redirect (next_page) if next_page else redirect(url_for('index'))
       else:
           flash('Login unsuccessful', 'danger')
    return render_template('login.html', title = 'Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has benn created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New post', form=form, legend='New post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post was updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update post',
                             form=form, legend='Update post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post was deleted', 'success')
    return redirect(url_for('index'))


@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike(post)
        db.session.commit()
    return redirect(request.referrer)