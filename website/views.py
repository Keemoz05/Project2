from flask import Blueprint, render_template, request, flash, jsonify,redirect,url_for
from flask_login import login_required, current_user
from .models import Lostitem
from .models import Founditem
from .models import User
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import os
import base64
import json

views = Blueprint('views', __name__)
replacementimage = os.path.join('static','noimageavailable.jpeg')

#allow file extensions
Allowed_File_Extensions = {'png', 'jpeg', 'jpg'}

def allow_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Allowed_File_Extensions

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():   #this function wil run whenever we go to "/"
    alllostitem = Lostitem.query.all()
    allfounditem = Founditem.query.all()
    req_lost_search = None
    req_found_search = None 

    if request.method == 'POST':
        search_query = request.form.get('search')

        if search_query:
            req_lost_search = Lostitem.query.filter(Lostitem.name.contains(search_query)).all()
            req_found_search = Founditem.query.filter(Founditem.name.contains(search_query)).all()

    
    return render_template("home.html", user=current_user,lostitem=req_lost_search if req_lost_search is not None else alllostitem,founditem=req_found_search if req_found_search is not None else allfounditem,userdatabase=User,replacementimage=replacementimage)



@views.route('/delete-lostitem', methods=['POST'])
def delete_lostitem():  
    lostitem = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    lostitemid = lostitem['lostitemid']
    lostitem = Lostitem.query.get(lostitemid)
    if lostitem:
        if lostitem.user_id == current_user.id:
            db.session.delete(lostitem)
            db.session.commit()
        elif current_user.first_name == 'Admin':
            db.session.delete(lostitem)
            db.session.commit()

    return jsonify({})

@views.route('/delete-founditem', methods=['POST'])
def delete_founditem():  
    founditem = json.loads(request.data) #this function expects a JSON from the INDEX.js file 
    founditemid = founditem['founditemid']
    founditem = Founditem.query.get(founditemid)
    if founditem:
        if founditem.user_id == current_user.id:
            db.session.delete(founditem)
            db.session.commit()
        elif current_user.first_name == 'Admin':
            db.session.delete(founditem)
            db.session.commit()

    return jsonify({})
@views.route('/reportitem')
@login_required
def reportitempage():

    return render_template("reportitem.html",user=current_user)
  

@views.route('/reportfounditem',methods=['GET', 'POST'])
@login_required
def reportfounditempage():

    if request.method == 'POST': 
        picture = request.files['pic']
        itemname = request.form.get('name')
        itemdescription = request.form.get('description')
        location = request.form.get('location')
        imagebase64 = ''
        if picture.filename:
            imagebase64 = picture.read()
            imagebase64 = base64.b64encode(imagebase64)
        if len(itemname) < 1:
            flash('Item is too short!', category='error')
        elif not allow_file(picture.filename) and picture.filename != '':
            flash('Invalid file type! Only PNG, JPEG and JPG are allowed.',category='error')
        else:
            new_founditems = Founditem(name=itemname,description=itemdescription, user_id=current_user.id,image_file=imagebase64,location=location)  #providing the schema for the note 
            db.session.add(new_founditems) #adding the note to the database 
            db.session.commit()
            flash('Found Item added!', category='success')
            return redirect(url_for('views.usersettings'))
    itemname = request.form.get('name','')
    itemdescription = request.form.get('description','')
    location = request.form.get('location','')    
    return render_template("reportfounditem.html",user=current_user,replacementimage=replacementimage,itemname=itemname,itemdescription=itemdescription,location=location)

@views.route('/reportlostitem',methods=['GET', 'POST'])
@login_required
def reportlostitempage():
    if request.method == 'POST': 
        picture = request.files['pic']
        itemname = request.form.get('name')
        itemdescription = request.form.get('description')
        location = request.form.get('location')
        imagebase64 = ''
        if picture.filename:
            imagebase64 = picture.read()
            imagebase64 = base64.b64encode(imagebase64)
        if len(itemname) < 1:
            flash('Item is too short!', category='error') 
        elif not allow_file(picture.filename) and picture.filename != '':
            flash('Invalid file type! Only PNG, JPEG and JPG are allowed.',category='error')
        else:               
            new_lostitems = Lostitem(name=itemname,description=itemdescription, user_id=current_user.id,image_file=imagebase64,location=location)  #providing the schema for the note 
            db.session.add(new_lostitems) #what if i assign a homeid?
            db.session.commit()
            flash('Lost Item added!', category='success')      
            return redirect(url_for('views.usersettings'))
    itemname = request.form.get('name','')
    itemdescription = request.form.get('description','')
    location = request.form.get('location','')            
    return render_template("reportlostitem.html",user=current_user,replacementimage=replacementimage,itemname=itemname,itemdescription=itemdescription)

@views.route('/user-settings',methods=['GET','POST'])
@login_required
def usersettings():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        contactinfo = request.form.get('contactinfo')
        user = User.query.filter_by(email=current_user.email).first()
        user.email = email
        user.first_name = first_name
        if password != '':
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        user.contactinfo = contactinfo
        flash('Your information has been saved!',category='info')
        db.session.commit()
    return render_template("usersettings.html",user=current_user,email=current_user.email,first_name=current_user.first_name,contactinfo=current_user.contactinfo,replacementimage=replacementimage)

@views.route('/lostitem/<int:lostitem_id>', methods=['GET', 'POST'])
def display_lostitem(lostitem_id):
    thislostitem = Lostitem.query.get(lostitem_id)
    return render_template('displaylostitem.html',user=current_user,thislostitem=thislostitem,replacementimage=replacementimage,userdatabase=User)

@views.route('/founditem/<int:founditem_id>', methods=['GET', 'POST'])
def display_founditem(founditem_id):
    thisfounditem = Founditem.query.get(founditem_id)
    return render_template('displayfounditem.html',user=current_user,thisfounditem=thisfounditem,replacementimage=replacementimage,userdatabase=User)