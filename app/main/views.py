#!/user/bin/env python
# -*- coding:utf-8 -*-
# author:ZRui
# datetime:2018/10/24 23:25
# software:PyCharm
from datetime import datetime
from . import main
from flask import render_template, url_for, redirect, session, flash, request, current_app, jsonify
from .forms import PostForm, EditForm
from .. import db
from ..models import User, Post, Category, Like
from flask_login import current_user, login_required


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    category_count = Category.count()
    return render_template('index.html', posts=posts, pagination=pagination, category_count=category_count)


@main.route('/about')
def about():
    liked = Like.query.first()
    return render_template('about.html', liked=liked)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@main.route('/category/<int:id>')
def category(id):
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(id)
    pagination = category.posts.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('category_search.html', category=category, posts=posts, pagination=pagination)

@main.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(tag=form.category.data).first()
        if category is None:
            category = Category(tag=form.category.data)
            db.session.add(category)
            db.session.commit()
        post=Post(title=form.title.data,
                  body=form.body.body,
                  summary=form.summary.data,
                  user=User.query.first(),
                  category=category)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', id=post.id))
    return render_template('write.html', form=form, the_category=Category.query.all())

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = EditForm()
    post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.summary.data = post.summary
    return render_template('edit.html', form=form)

@main.route('/like')
def like():
    liked = Like.query.first()
    liked.count += 1
    db.session.add(liked)
    db.session.commit()
    return jsonify({'liked': liked.count})