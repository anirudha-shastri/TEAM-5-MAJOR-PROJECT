import base64
from flask_login.utils import login_required
from dat import app ,mail ,bcrypt
from flask import render_template, redirect, url_for,flash, request
from dat.models import User,Img, Img_Annotated, Img_Auto_Ann
from dat import db
from dat.forms import ChangePasswordForm, ConfirmDeleteAccount, RegisterForm, LoginForm ,RequestResetForm ,ResetPasswordForm, ConfirmCurrentPassword
from flask_login import login_user,logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import cv2
import ast
import numpy as np
from flask_mail import Message
import pandas as pd
from csv import writer 

import matplotlib
matplotlib.use('Agg')
from dat.bone_age_funcs import draw_keypoints_on_image,predict
from dat.ann_tool_funcs import auto_full_anno

@app.route("/")
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route("/tools")
@login_required
def tools_page():
    return render_template('tools.html')

def send_verify_email(user):
    token = user.get_reset_token()
    msg = Message('Confirm your e-mail',
                  sender='noreply@demo.com',
                  recipients=[user.email_address])
    msg.body = f'''To verify your account, visit the following link:
{url_for('verify_token', token=token, _external=True)}
This link will be valid for 30 minutes.
If you did not make this request then simply ignore this email
'''
    mail.send(msg)

@app.route("/verify_email", methods=['GET', 'POST'])
def verify_request():
    user = current_user
    send_verify_email(user)
    flash(f'An email has been sent to {user.email_address} for verification', category='info')
    return redirect(url_for('acc_settings_page'))
      

@app.route("/verify_account/<token>", methods=['GET', 'POST'])
def verify_token(token):
    # if current_user.is_authenticated:
    #     flash('Your e-mail has been verified!', category ="success")
    #     return redirect(url_for('home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('login_page'))
    else:
        user.email_verified()
        flash('Your e-mail has been verified!', category ="success")
    return redirect(url_for('acc_settings_page'))

        
        
     

@app.route('/register', methods = ['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address = form.email_address.data).first()
        if user:
            flash(f'Email you entered already exists!',"danger")
        else:    
            user_to_create = User(username = form.username.data,
                              email_address = form.email_address.data,
                              password = form.password1.data)
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category= "success")

            # send_verify_email(user_to_create)
            # flash(f'A link has been sent to your email with instructions to verify your account.',category="info")

            return redirect(url_for('tools_page')) 
    if form.errors != {}:    #if  errors from validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category = 'danger')
    return render_template('register.html', form = form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username= form.username.data).first()
        if not(attempted_user):
            flash("There is no account with that username",category="danger")
            return redirect(url_for("login_page"))
        if attempted_user and attempted_user.check_password_correction(
                attempted_password = form.password.data
        ):
            login_user(attempted_user)
            flash(f'Successfully logged in! Welcome {attempted_user.username}', category= 'success')
            return redirect(url_for('tools_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')
    return render_template('login.html', form = form)

@app.route('/boneAge1')
@login_required
def bone_age1_page():
    return render_template('boneAge1.html')



@app.route('/boneAge2',methods=['POST','GET'])
@login_required
def bone_age2_page():
    # uploading normal img to Img class
    pic = request.files['pic']
    pic_ann = pic.read()        #converting input image to filestorage type
    npimg = np.fromstring(pic_ann,np.uint8) #converting to necessary form to send to imdecode
    
    if not pic:
        flash('Please select an image to continue', category = "danger")
        return render_template('ceph_annotate1.html')
        # return redirect(url_for('ceph_annotate2_page'))

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    #saving input img to db
    user_id = current_user.id
    input_img = Img(user_id=user_id,img=pic_ann, name=filename, mimetype=mimetype)
    db.session.add(input_img)
    db.session.commit()
    # flash('Image successfully uploaded', category='success')

    

    image = cv2.imdecode(np.frombuffer(npimg, np.uint8), cv2.IMREAD_COLOR)
    res=cv2.resize(image,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_CUBIC)
    pic_resize = res[400:1000,0:250]
    converted_img = cv2.imencode('.jpg',pic_resize)[1].tostring()
    image, keypoints = predict(converted_img)
    draw_keypoints_on_image(image, keypoints, filename)
    
    flash('annotated image saved',category= "success")
    return redirect(url_for('bone_age1_page'))



@app.route('/ann_tool',methods=['POST','GET'])
@login_required
def ann_tool_page():
    return render_template('annTool.html')


@app.route('/annTool2',methods=['POST','GET'])
@login_required
def ann_tool2_page():
    
    # uploading normal img to Img class
    pic = request.files['pic']
    pic_ann = pic.read()        #converting input image to filestorage type
    npimg = np.fromstring(pic_ann,np.uint8) #converting to necessary form to send to imdecode
    

   
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400
    image = cv2.imdecode(np.frombuffer(npimg, np.uint8), cv2.IMREAD_COLOR) #converting img from filestorage type to np array


    x_vals =[]
    y_vals =[]
    annotation_vals = []
    res=cv2.resize(image,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_CUBIC)
   




    #implemeting crop
    image_final = res[400:1000,0:250]
    # ref_image=res[400:1000,0:250]

    auto_full_anno(image_final,x_vals,y_vals,annotation_vals, image, filename)
   
    
    return render_template('stage.html',filename = filename, x_vals= x_vals, y_vals = y_vals, annotation_vals = annotation_vals )

@app.route('/stage_select',methods=['GET','POST'])
@login_required
def select_stage():
    if request.method == 'POST':
        stage = request.form['stage']
        filename = request.form['filename']

        # getting x,y and ann coords in str type from form
        x_vals_str = request.form['x_vals']
        
        y_vals_str = request.form['y_vals']
        annotation_vals_str = request.form['annotation_vals']
        
        
        # converting from str to list
        x_vals = ast.literal_eval(x_vals_str)
        y_vals = ast.literal_eval(y_vals_str) 
        annotation_vals = ast.literal_eval(annotation_vals_str)
        
      
        data = {'X':x_vals,'Y':y_vals,'Annotation':annotation_vals}
        df= pd.DataFrame(data)
        temp_n='dat/csv/'+'{}'.format(filename.replace('.jpg',''))+'.csv'
        with open(temp_n, 'w') as f_object:
                n_temp='annotations'+'---'+filename+'-----'+stage
                temp_l=['X','Y',n_temp]
                writer_object = writer(f_object)  
                writer_object.writerow(temp_l)
                for i in range(len(df)):
                            temp_l=[df.iloc[i][0],df.iloc[i][1],df.iloc[i][2]]
                            writer_object = writer(f_object)  
                            writer_object.writerow(temp_l)
        f_object.close()
        flash('CSV file stored successfully!', category= 'success')
    return redirect(url_for('ann_tool_page'))


@app.route('/displayImg')
@login_required
def ann_img_list():
    # ########displaying one image from db using conversion to base64 (works)#########     (DO NOT DELETE)
    # #get image object
    # img_obj = Img.query.filter_by(id=1).first()

    # #get byte data from that object
    # img = img_obj.img
    # # print(type(img))
    
    # #convert BLOB(byte) to base64
    # img = base64.b64encode(img)

    # #decode it to utf-8
    # img = img.decode("UTF-8")
    # # print(img)

    ########display multiple imgs from db

    images = Img_Annotated.query.all()
    
    return render_template('annImageList.html',images = images)

@app.route('/view', methods = ['POST'])
@login_required
def view_ann_img():
    #getting the id of the requested image for download
    img_id = request.form["img-id"]
        
    #get image object
    img_obj = Img_Annotated.query.filter_by(id=img_id).first()

    #get byte data from that object
    img1 = img_obj.img1

    
    #convert BLOB(byte) to base64
    img1 = base64.b64encode(img1)

        #decode it to utf-8
    img1 = img1.decode("UTF-8")
      
    #second img
    #get byte data from that object
    img2 = img_obj.img2
    
    
    #convert BLOB(byte) to base64
    img2 = base64.b64encode(img2)

        #decode it to utf-8
    img2 = img2.decode("UTF-8")

    
    
    return render_template('viewAnnImage.html',image1=img1, image2=img2)

#Account settings 

@app.route("/accountSettings")
@login_required
def acc_settings_page():
    return render_template('accSettings.html',user=current_user)


@app.route('/logout')
def logout_page():
    logout_user()

    # flash("You have been logged out!", category ='info')
    return redirect(url_for('home_page'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email_address])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
This link will be valid for 30 minutes.
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user is None:
            flash('The email you entered isn\'t registered with any account', category="danger")
        else:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password. If you didnt find it, please check spam folder', category='info')
    
        return redirect(url_for('login_page'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # hashed_password = form.password.data
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login_page'))
    if form.errors != {}:    #if  errors from validations
        for err_msg in form.errors.values():
            flash(f'Couldn\'t reset password: {err_msg}', category = 'danger')
        
        return redirect(url_for('reset_request'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/changePassword1',methods=['GET', 'POST'])
@login_required
def change_password1():
    form = ConfirmCurrentPassword()
    
    if form.validate_on_submit():
        if not current_user.check_password_correction(attempted_password = form.old_password.data):
            flash(f'The old password you entered is incorrect', category = "danger")
            return redirect(url_for('change_password1'))
        else:
            return redirect(url_for('change_password2'))
            




    return render_template('changePassword.html',form = form)

@app.route('/changePassword2',methods=['GET', 'POST'])
@login_required
def change_password2():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.commit()
        flash(f"Password changed successfully", category= "success")

        return redirect(url_for('acc_settings_page')) 
    if form.errors != {}:    #if  errors from validations
        for err_msg in form.errors.values():
            flash(f'Couldn\'t change password {err_msg}', category = 'danger')
           
            return render_template('changePassword2.html',form = form)

@app.route('/deleteAccount1',methods=['GET', 'POST'])
@login_required
def delete_account1():
    form = ConfirmCurrentPassword()
    
    if form.validate_on_submit():
        if not current_user.check_password_correction(attempted_password = form.old_password.data):
            flash(f'The password you entered is incorrect', category = "danger")
            return redirect(url_for('delete_account1'))
        else:
            return redirect(url_for('delete_account2'))
            




    return render_template('deleteAccount.html',form = form)

@app.route('/deleteAccount2',methods=['GET', 'POST'])
@login_required
def delete_account2():
    form = ConfirmDeleteAccount()
    
    user_to_delete = User.query.filter_by(id = current_user.id).first()
    if form.validate_on_submit():
        try:
            # auto_img_delete = Img_Auto_Ann.query.filter_by(user_id=current_user.id).all()
            # ann_img_delete = Img_Annotated.query.filter_by(user_id = current_user.id).all()
            # img_delete = Img.query.filter_by(user_id=current_user.id).all()
            Img_Auto_Ann.query.filter_by(user_id=current_user.id).delete()
            Img_Annotated.query.filter_by(user_id = current_user.id).delete()
            Img.query.filter_by(user_id=current_user.id).delete()
            # db.session.delete(auto_img_delete)
            # db.session.commit()
            # db.session.delete(img_delete)
            # db.session.commit()
            # db.session.delete(ann_img_delete)
            # db.session.commit()
            db.session.delete(user_to_delete)
            db.session.commit()
        except:
            flash("Error! Couldn't delete account",category='danger')
            return redirect(url_for('delete_account1'))
        # flash(f'', category = "info")
        return redirect(url_for('home_page'))
    # else:
    #         return redirect(url_for('delete_account2'))
            




    return render_template('deleteAccount2.html',form =form)