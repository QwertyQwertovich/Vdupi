# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
import models
main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, mail=current_user.email)

@main.route('/messages')
@login_required
def messages_load():
    chats = models.db.query(models.Chats).filter_by(frm=current_user.id).all()
    rt = []
    names=[]
    for i in chats:
        rt.append(str(i.to))
        print(models.db.query(models.User).filter_by(id=i.to).first())
        names.append(models.db.query(models.User).filter_by(id=i.to).first().name)
    print(rt)
    return render_template('messages.html', name=current_user.name, mail=current_user.email, id=current_user.id, rt=rt,ln=len(rt),names=names)

@main.route('/messager/<int:fr_id>/')
@login_required
def chat_load(fr_id):
    return render_template('messager.html', name=current_user.name, mail=current_user.email, id=current_user.id, )