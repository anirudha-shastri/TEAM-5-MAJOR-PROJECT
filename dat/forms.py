from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from dat.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by( username = username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    username = StringField(label='User Name:',validators=[Length(min=2, max =30), DataRequired()])
    email_address = StringField(label='Email Address:',validators=[Email(),DataRequired()])
    password1 = PasswordField(label = 'Password:', validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label = 'Confirm Password:',validators=[EqualTo('password1'),DataRequired()])
    submit = SubmitField(label = 'CREATE ACCOUNT')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label = 'SIGN IN')

class RequestResetForm(FlaskForm):
    email_address = StringField(label ='Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# Forgot password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[Length(min=6),DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# Change password forms
class ConfirmCurrentPassword(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    submit = SubmitField('Next')

class ChangePasswordForm(FlaskForm):
    
    new_password = PasswordField("New Password", validators=[Length(min = 6),DataRequired()] )
    confirm_new_password = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo('new_password')])
    submit = SubmitField('Submit Changes')

#delete user account
class ConfirmDeleteAccount(FlaskForm):
    submit = SubmitField('Delete')