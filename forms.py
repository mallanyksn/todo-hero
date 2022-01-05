from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,PasswordField

class ContactForm(FlaskForm):
	name = StringField(label='Name',validators=[])
	email = StringField(label='Email',validators=[])
	msg = TextAreaField(label='Message/Issue',validators=[])
	suggestion = StringField(label='Suggestion(*optional)',validators=[])