from dat import db, app
from dat import bcrypt
from dat import login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(length=30),nullable=False,unique=True)
    email_address= db.Column(db.String(length=50),nullable=False, unique= True)
    password_hash= db.Column(db.String(length=60),nullable= False)
    is_verified=db.Column(db.Boolean(),nullable=False, default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(int(user_id))

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
        
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def email_verified(self):
        self.is_verified = True
        db.session.commit()

    # def get_id(self):
    #     return (self.user_id)

# annotation tool 
class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    dt = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

class Img_Annotated(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    img1 = db.Column(db.Text, nullable=False)
    name1 = db.Column(db.Text, nullable=False)
    img2 = db.Column(db.Text, nullable=False)
    name2 = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False, default= "image/jpeg")
    dt = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

# Bone Age 
class Img_Auto_Ann(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)

db.create_all()