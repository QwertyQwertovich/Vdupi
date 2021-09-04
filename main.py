# main.py
import vk_api
import requests
from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
import models
from PIL import Image
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os.path
import platform

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
            if im.size[0] == im.size[1]:
                vk = vk_api.VkApi(
                    token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
                owneruploadurl = vk.method("photos.getUploadServer", {"group_id": 206800941, "album_id": 281114517})[
                    'upload_url']
                if platform.system() == "Windows":
                    ownerfile_ = {'photo': ('last_ava.jpg', open(r'static\images\last_ava.jpg', 'rb'))}
                else:
                    ownerfile_ = {'photo': ('last_ava.jpg', open(r'static/images/last_ava.jpg', 'rb'))}
                ownerr = requests.post(owneruploadurl, files=ownerfile_)
                res = vk.method("photos.save",
                                {"album_id": 281114517, "group_id": 206800941, "caption": str(current_user.id),
                                 "server": ownerr.json()["server"], "photos_list": ownerr.json()["photos_list"],
                                 "hash": ownerr.json()["hash"]})
                user = models.db.query(models.User).filter_by(id=current_user.id).first()
                user.have_profile_picture = 1
                user.photo = str(res[0]["owner_id"]) + '_' + str(res[0]["id"])
                models.db.commit()
                flash('Photo uploaded successfully')
            else:
                flash('Photo should have 1:1 ratio')
        except Exception as e:
            flash('Error: ' + str(e))
        return redirect('profile')
    else:
        try:
            img = vk.method("photos.getById",
                            {"photos": models.db.query(models.User).filter_by(id=current_user.id).first().photo})[0][
                'sizes'][-1]['url']
        except:
            img = "https://sun9-49.userapi.com/impg/BZYeU9FNE98iPqctPNL8FX7EwxyaajS6PaYaXA/dkCGd23VNKQ.jpg?size=256x256&quality=96&sign=a31256d23fe76d7f750af50eaefaab60&c_uniq_tag=03KAYcv7yvO3-bVDwzRvdjWdpNr6u_864F6oFlXb20k&type=album"

        return render_template('profile.html', name=current_user.name, mail=current_user.email, img=img,
                               id=current_user.id)


@main.route('/messages', methods=["POST", "GET"])
@login_required
def messages_load():
    if request.method == "POST":
        try:
            text = request.form["textarea"]
            fr_id = int(text)
            frm = current_user.id
            to = fr_id
            if fr_id <= len(models.db.query(models.User).all()):
                new_chat = models.Chats(frm=frm, to=to)
                models.db.add(new_chat)
                new_chat = models.Chats(frm=to, to=frm)
                models.db.add(new_chat)
                models.db.commit()
                date = datetime.utcnow()
                flash("Message sent")
                return redirect("/messager/" + str(fr_id) + "/")
        except Exception as e:
            flash("Error: " + str(e))
        return redirect("/messages")
    chats = models.db.query(models.Chats).filter_by(frm=current_user.id).all()
    rt = []
    names = []
    img = []
    colors = []
    for i in chats:
        messages = models.db.query(models.Message).filter_by(to=current_user.id).all()
        color = "is-light"
        for j in messages:
            if j.is_read == 0 and j.frm == i.to:
                color = "is-dark"
        colors.append(color)
        vk = vk_api.VkApi(token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
        if models.db.query(models.User).filter_by(id=i.to).first().have_profile_picture == 1:
            img.append(
                vk.method("photos.getById", {"photos": models.db.query(models.User).filter_by(id=i.to).first().photo})[
                    0]['sizes'][0]['url'])
        else:
            img.append(
                "https://sun9-49.userapi.com/impg/BZYeU9FNE98iPqctPNL8FX7EwxyaajS6PaYaXA/dkCGd23VNKQ.jpg?size=256x256&quality=96&sign=a31256d23fe76d7f750af50eaefaab60&c_uniq_tag=03KAYcv7yvO3-bVDwzRvdjWdpNr6u_864F6oFlXb20k&type=album")
        rt.append(str(i.to))
        names.append(models.db.query(models.User).filter_by(id=i.to).first().name)
    return render_template('messages.html', name=current_user.name, mail=current_user.email, id=current_user.id, rt=rt,
                           ln=min(len(rt), 20), names=names, img=img, colors=colors)


@main.route('/messager/<int:fr_id>/', methods=["POST", "GET"])
@login_required
def chat_load(fr_id):
    if request.method == "GET":
        try:
            sticker = request.args.get('sticker', '')
            if sticker == '':
                pass
            else:
                flash("Message sent")
                frm = current_user.id
                to = fr_id
                attachments = ''
                new_msg = models.Message(text='', frm=frm, to=to, attachments=attachments, is_sticker=sticker,
                                         date=datetime.utcnow())
                models.db.add(new_msg)
                models.db.commit()
                return redirect("/messager/" + str(fr_id) + "/")
        except Exception as e:
            print(e)
            flash("Error: " + str(e))
    if request.method == "POST":
        try:
            text = request.form["textarea"]
            frm = current_user.id
            to = fr_id
            attachments = ''
            new_msg = models.Message(text=text, frm=frm, to=to, attachments=attachments, date=datetime.utcnow())
            models.db.add(new_msg)
            models.db.commit()
            return redirect("/messager/" + str(fr_id) + "/")
        except Exception as e:
            flash("Error: " + str(e))
        return redirect("/messager/" + str(fr_id) + "/")
    try:
        messages = models.db.query(models.Message).all()
        for i in messages:
            if i.to == current_user.id and i.is_read == 0:
                i.is_read = 1
        models.db.commit()
        msg = []
        ava_me = "https://sun9-49.userapi.com/impg/BZYeU9FNE98iPqctPNL8FX7EwxyaajS6PaYaXA/dkCGd23VNKQ.jpg?size=256x256&quality=96&sign=a31256d23fe76d7f750af50eaefaab60&c_uniq_tag=03KAYcv7yvO3-bVDwzRvdjWdpNr6u_864F6oFlXb20k&type=album"
        ava_fr = 'https://sun9-49.userapi.com/impg/BZYeU9FNE98iPqctPNL8FX7EwxyaajS6PaYaXA/dkCGd23VNKQ.jpg?size=256x256&quality=96&sign=a31256d23fe76d7f750af50eaefaab60&c_uniq_tag=03KAYcv7yvO3-bVDwzRvdjWdpNr6u_864F6oFlXb20k&type=album'
        vk = vk_api.VkApi(token="85e6cd0772f653585f2e4a9c1424219e71b31405aee84057d28996899ca68c4023ecf98e63185edb0fdd7")
        if models.db.query(models.User).filter_by(id=current_user.id).first().have_profile_picture == 1:
            ava_me = vk.method("photos.getById",
                               {"photos": models.db.query(models.User).filter_by(id=current_user.id).first().photo})[0][
                'sizes'][0]['url']
        if models.db.query(models.User).filter_by(id=fr_id).first().have_profile_picture == 1:
            ava_fr = \
                vk.method("photos.getById", {"photos": models.db.query(models.User).filter_by(id=fr_id).first().photo})[
                    0][
                    'sizes'][0]['url']
        for i in messages:
            if (i.frm == current_user.id and i.to == fr_id) or (i.to == current_user.id and i.frm == fr_id):
                if i.frm == current_user.id:
                    if i.is_read == 1:
                        color = "is-light"
                    else:
                        color = "is-dark"
                    ava = ava_me
                    name = models.db.query(models.User).filter_by(id=current_user.id).first().name
                else:
                    color = "is-warning"
                    ava = ava_fr
                    name = models.db.query(models.User).filter_by(id=fr_id).first().name
                is_read = i.is_read
                is_sticker = i.is_sticker
                st_path = ""
                if is_sticker != 0:
                    pack = is_sticker // 1000
                    sticker = is_sticker % 1000
                    st_path = "/static/stickers/pack" + str(pack) + "/" + str(sticker) + ".png"
                print(st_path != '')
                text = i.text
                msg.append([color, ava, name, text, st_path])
    except Exception as e:
        flash("Error: " + str(e))
        return redirect("/messages")
    return render_template('messager.html', name=current_user.name, mail=current_user.email, id=current_user.id,
                           msg=msg, ln=min(2000, len(msg)),
                           name2=models.db.query(models.User).filter_by(id=fr_id).first().name, id2=fr_id)


@main.route('/sticker/<int:fr_id>/', methods=["POST", "GET"])
@login_required
def sticker_add(fr_id):
    if request.method == "GET":
        try:
            pack = request.args.get('pack', '')
            if pack != '':
                pack = int(pack)
                if platform.system()=="Windows":
                    path = "static\\stickers\\pack" + str(pack)
                else:
                    path = "static/stickers/pack" + str(pack)
                num_files = len([f for f in os.listdir(path)
                                 if os.path.isfile(os.path.join(path, f))])
                stickers = [{"id": str(pack) + str(i).zfill(3),
                             "path": "/static/stickers/pack" + str(pack) + "/" + str(i) + ".png", "text": ''} for i in
                            range(num_files)]
                return render_template('sticker.html', name=current_user.name, mail=current_user.email,
                                       id=current_user.id, st=stickers, ln=len(stickers), fr_id=fr_id, pack=pack,
                                       is_pack_selector=0)
        except Exception as e:
            print(e)
            flash("Error: " + str(e))
    pack_ln = 13
    pack_ln += 1
    stickers = [
        {"id": str(i) + str(0).zfill(3), "path": "/static/stickers/pack" + str(i) + "/" + str(0) + ".png", "text": '',
         "href": "/sticker/" + str(fr_id) + "?pack=" + str(i)} for i in range(1, pack_ln)]
    return render_template('sticker.html', name=current_user.name, mail=current_user.email,
                           id=current_user.id, st=stickers, ln=len(stickers), fr_id=fr_id, is_pack_selector=1)


@main.route('/apii', methods=["POST", "GET"])
@login_required
def apii():
    messages = models.db.query(models.Message).filter_by(to=current_user.id).all()
    r = "False"
    for j in messages:
        if j.is_read == 0:
            r = str(j.date)
            print(r)
    return r


@main.route('/api', methods=["POST", "GET"])
def api():
    if request.method == "GET":
        try:
            method = request.args.get('method', '')
            if method == "getApiKey":
                mail = request.args.get('mail', '')
                password = request.args.get('password', '')
                user = models.db.query(models.User).filter_by(email=mail).first()
                print(mail, password, check_password_hash(user.password, password))
                if check_password_hash(user.password, password):
                    return user.api_key
                else:
                    return "Error Bad password"
            # print(method, method == "getApiKey", str(method) == "getApiKey")
            if method == "getPublicUserInfo":
                user_id = request.args.get('user_id', '')
                user = models.db.query(models.User).filter_by(id=user_id).first()
                return {"id": user.id, "photo": user.photo, "have_profile_picture": user.have_profile_picture,
                        "name": user.name, "reg_date": user.reg_date, "desc": user.desc,
                        "is_banned": user.is_banned}
            if method == "getUserInfo":
                api_key = request.args.get('api_key', '')
                user = models.db.query(models.User).filter_by(api_key=api_key).first()
                return {"id": user.id, "photo": user.photo, "have_profile_picture": user.have_profile_picture,
                        "email": user.email, "name": user.name, "reg_date": user.reg_date, "desc": user.desc,
                        "is_banned": user.is_banned}
            if method == "getChats":
                api_key = request.args.get('api_key', '')
                user = models.db.query(models.User).filter_by(api_key=api_key).first()
                id = user.id
                chats = models.db.query(models.Chats).filter_by(frm=id).all()
                return str([i.to for i in chats])
            if method == "getMessages":
                api_key = request.args.get('api_key', '')
                to = request.args.get('id', '')
                user = models.db.query(models.User).filter_by(api_key=api_key).first()
                id = user.id
                msg = []
                messages = models.db.query(models.Message).all()
                for i in messages:
                    if i.frm == id or i.to == id:
                        msg.append({"id": i.id, "from": i.frm, "to": i.to, "text": i.text, "attachments": i.attachments,
                                    "date": i.date, "is_read": i.is_read, "is_sticker": i.is_sticker})
                return {"messages": msg}
        except Exception as e:
            return "Error" + str(e)
    return "Error wtf"
