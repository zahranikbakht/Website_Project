import csv
import bcrypt as bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, SelectField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email
from flask import Flask, session, redirect, render_template, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)

# login initialize
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# email initialize
app.config['SECRET_KEY'] = 'zahra nikbakht'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soen287website@gmail.com'  # enter your email here
app.config['MAIL_DEFAULT_SENDER'] = 'soen287website@gmail.com'  # enter your email here
app.config['MAIL_PASSWORD'] = 'Soen287Website'  # enter your password here
mail = Mail(app)


# function for a protected page where you can see the messages sent by users
@app.route('/messages')
@login_required
def messages():
    prefix = '/static/'
    with open('data/messages.csv') as f:
        top_list = list(csv.reader(f))[1:]
    return render_template('messages.html', top_list=top_list, prefix=prefix)


# function for homepage, including the login form for admins
@app.route('/', methods=['GET', 'POST'])
def home():
    form = LoginForm()
    prefix = '/static/'
    if form.validate_on_submit():
        user = find_user(form.username.data)
        # checking if the credentials are valid to login the admin
        if user and bcrypt.checkpw(form.password.data.encode(), user.password.encode()):
            flash('Logged in successfully.')
            login_user(user)
            session['next'] = '/'
            return redirect("/")
        else:
            flash('Incorrect username and password.')
    with open('data/top3.csv') as f:
        top_list = list(csv.reader(f))[1:4]
    return render_template('home.html', top_list=top_list, prefix=prefix, form=form)


@app.route('/about')
def about():
    return render_template('about.html')


# function for a page for released games
# including ratings for all games which are dynamically calculated based on user reviews
@app.route('/released')
def released():
    bb = 0
    ww = 0
    tq = 0
    kp = 0
    count = 0
    with open('data/review.csv') as f:
        reviewlist = list(csv.reader(f))

    # calculating rating for Black Butterflies
    for row in reviewlist:  # getting all the rows that include rating for this game
        temp = 0
        if row and row[0] == "Black Butterflies":
            count += 1
            for i in range(6):
                temp += int(row[i + 1])  # adding the scores
        bb += (temp / 6.0)
    if count != 0:
        bb = bb / count     # calculating the average score
    bb = round(bb, 2)
    count = 0

    # calculating rating for Wonder's War
    for row in reviewlist:
        temp = 0
        if row and row[0] == "Wonder's War":
            count += 1
            for i in range(6):
                temp += int(row[i + 1])
        ww += (temp / 6.0)
    if count != 0:
        ww = ww / count
    ww = round(ww, 2)
    count = 0

    # calculating rating for Traitor's Quest
    for row in reviewlist:
        temp = 0
        if row and row[0] == "Traitor's Quest":
            count += 1
            for i in range(6):
                temp += int(row[i + 1])
        tq += (temp / 6.0)
    if count != 0:
        tq = tq / count
    tq = round(tq, 2)
    count = 0

    # calculating rating for Kitty Pop
    for row in reviewlist:
        temp = 0
        if row and row[0] == "Kitty Pop":
            count += 1
            for i in range(6):
                temp += int(row[i + 1])
        kp += (temp / 6.0)
    if count != 0:
        kp = kp / count
    kp = round(kp, 2)
    return render_template('releasedGames.html', bb=bb, ww=ww, tq=tq, kp=kp)


@app.route('/wip')
def wip():
    return render_template('wip.html')


# function for contact page
# handling contact form
# featuring an email system to send an automatic reply to the user, letting them know that the message is received
@app.route('/contact', methods=['GET', 'POST'])
def handle_contact():
    form = ContactForm()
    if form.validate_on_submit():

        # defining the automatic reply message
        msg = Message("Message Received!", sender="soen287website@gmail.com", recipients=[str(form.email.data)])
        msg.body = "Hello " + form.name.data + "! Your message has been received and we will get back to you soon."
        mail.send(msg)
        flash('Thank you! We have sent you a confirmation email.')
        # collecting the data of the form and writing it in a .csv file
        with open('data/messages.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([form.name.data, form.email.data, form.game.data, form.message.data])
        return redirect(url_for('handle_contact'))
    else:
        return render_template('contact.html', form=form)


# function for a review survey (dynamic URL based on the game)
# handles reviews from the user
@app.route('/review/<game>', methods=['GET', 'POST'])
def review(game):
    form = ReviewForm()
    if form.validate_on_submit():
        flash('Thank you for your participation!')
        # collecting the data of the form and writing it in a .csv file
        with open('data/review.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(
                [game, form.one.data, form.two.data, form.three.data, form.four.data, form.five.data, form.six.data])
        return redirect(url_for('home'))
    else:
        return render_template("review.html", form=form, game=game)


# user class (for admins only)
class User(UserMixin):
    def __init__(self, username, password=None):
        self.id = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    user = find_user(user_id)
    if user:
        user.password = None
    return user


def find_user(username):
    with open('data/users.csv') as f:
        for user in csv.reader(f):
            if username == user[0]:
                return User(*user)
    return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect('/')


# the contact form included in contact page
class ContactForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    email = EmailField(validators=[InputRequired(), Email()])
    message = TextAreaField(validators=[InputRequired()], render_kw={'rows': 7})
    game = SelectField(validators=[InputRequired()],
                       choices=[('Black Butterflies', 'Black Butterflies'), ("Wonder's War", "Wonder's War"),
                                ("Traitor's Quest", "Traitor's Quest"), ("Kitty Pop", "Kitty Pop"),
                                ("Salad Story", "Salad Story"),
                                ("Dream of Desert", "Dream of Desert"), ("Unreality", "Unreality")])
    submit = SubmitField('Submit')


# the login form included in homepage
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


# review form
class ReviewForm(FlaskForm):
    one = RadioField('What do you think about the story?', validators=[InputRequired()],
                     choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    two = RadioField('What do you think about the music?', validators=[InputRequired()],
                     choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    three = RadioField('What do you think about the general gameplay?', validators=[InputRequired()],
                       choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    four = RadioField('What do you think about the characters?', validators=[InputRequired()],
                      choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    five = RadioField('If a friend asked you how the game was, what would you say?', validators=[InputRequired()],
                      choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    six = RadioField('How was the game compared to other games that you have played in the same genre?',
                     validators=[InputRequired()],
                     choices=[('5', 'Excellent'), ('4', 'Good'), ('3', 'Mediocre'), ('2', 'Bad'), ('1', 'Terrible')])
    submit = SubmitField('submit')


if __name__ == '__main__':
    app.run()
