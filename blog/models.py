from datetime import datetime
from blog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user (user_id):
    return User.query.get(int(user_id))

likes = db.Table('likes',
    db.Column('user_liked', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_liked', db.Integer, db.ForeignKey('post.id'))
                 )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author',lazy=True)
    liker = db.relationship('Post', secondary=likes, backref=db.backref('liked_posts', lazy='dynamic'))

    def has_liked(self, post): # returns True is the user has liked some post
        #return self.liker.filter(likes.c.user_liked == self.id, likes.c.post_liked == post.id).count() > 0
        return db.session.query(likes).filter(likes.c.user_liked == self.id, likes.c.post_liked == post.id).count() > 0


    def like(self, post):
        if not self.has_liked(post):
            self.liker.append(post)
            #db.session.add(like)

    def unlike(self, post):
        if self.has_liked(post):
            self.liker.remove(post)

    def ___repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def ___repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"