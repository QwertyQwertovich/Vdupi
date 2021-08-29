# main.py
import vk_api
import requests
from flask import Blueprint, render_template,request,flash
from flask_login import login_required, current_user
import models
from PIL import Image
main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile', methods=["POST", "GET"])
@login_required
def profile():
    vk = vk_api.VkApi(token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
    if request.method == "POST":
        try:
            file = request.files['file']
            file.save("static/images/last_ava.jpg")
            im = Image.open('static/images/last_ava.jpg')
            if im.size[0]==im.size[1]:
                vk = vk_api.VkApi(token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
                owneruploadurl = vk.method("photos.getUploadServer", {"group_id": 206800941,"album_id":281114517})['upload_url']
                ownerfile_ = {'photo': ('last_ava.jpg', open(r'static\images\last_ava.jpg', 'rb'))}
                ownerr = requests.post(owneruploadurl, files=ownerfile_)
                res = vk.method("photos.save", {"album_id": 281114517, "group_id": 206800941, "caption": str(current_user.id), "server": ownerr.json()["server"], "photos_list": ownerr.json()["photos_list"], "hash": ownerr.json()["hash"]})
                user = models.db.query(models.User).filter_by(id=current_user.id).first()
                user.have_profile_picture = 1
                user.photo=str(res[0]["owner_id"])+'_'+str(res[0]["id"])
                models.db.commit()
                flash('Photo uploaded successfully')
            else:
                flash('Photo should have 1:1 ratio')
        except Exception as e:
            flash('Error: '+str(e))
        return render_template('profile.html', name=current_user.name, mail=current_user.email, img=vk.method("photos.getById", {"photos":models.db.query(models.User).filter_by(id=current_user.id).first().photo})[0]['sizes'][-1]['url'])
    else:
        return render_template('profile.html', name=current_user.name, mail=current_user.email, img=vk.method("photos.getById", {"photos":models.db.query(models.User).filter_by(id=current_user.id).first().photo})[0]['sizes'][-1]['url'])

@main.route('/messages')
@login_required
def messages_load():
    chats = models.db.query(models.Chats).filter_by(frm=current_user.id).all()
    rt = []
    names=[]
    img=[]
    for i in chats:
        vk = vk_api.VkApi(token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
        if models.db.query(models.User).filter_by(id=i.to).first().have_profile_picture ==1:
            img.append(vk.method("photos.getById", {"photos":models.db.query(models.User).filter_by(id=i.to).first().photo})[0]['sizes'][0]['url'])
        else:
            img.append("")
        rt.append(str(i.to))
        names.append(models.db.query(models.User).filter_by(id=i.to).first().name)
    return render_template('messages.html', name=current_user.name, mail=current_user.email, id=current_user.id, rt=rt,ln=min(len(rt), 20),names=names, img=img)

@main.route('/messager/<int:fr_id>/',)
@login_required
def chat_load(fr_id, methods=["POST", "GET"]):
    return render_template('messager.html', name=current_user.name, mail=current_user.email, id=current_user.id)