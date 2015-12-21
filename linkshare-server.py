import json
import time
import requests
import datetime
from flask import Flask, request, render_template
from database import DB

#import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment
from two1.lib.bitserv.payment_methods import BitTransfer
from two1.commands.config import Config

# set up server side wallet
app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)
username = Config().username

db = DB()


@app.route('/add', methods=['POST'])
@payment.required(1000)
def addLink():
    try:
        url = request.form['url']
        link_username = request.form['username']
        title = request.form['title']
        image = request.form['image']
        exists = db.submitted(url)
        if not exists:
            db.insert_link(url, link_username, title, image)
        else:
            return('Link already submitted\nTo upvote use: upvote <url>')
        return(db.get_post_list_string())
    except Exception as e:
        print(e)

@app.route('/upvote', methods=['POST'])
@payment.required(100)
def upvote():
    post_id = request.form['post_id']
    success, payee_username = db.upvote_link(post_id)
    if success:
        pay(payee_username, 100)
        return(db.get_post_list_string())
    else:
        return("No post with index %s" % str(post_id))


@app.route('/downvote', methods=['POST'])
@payment.required(100)
def downvote():
    post_id = request.form['post_id']
    success = db.downvote_link(post_id)
    if success:
        return(db.get_post_list_string())
    else:
        return("No post with index %s" % str(post_id))


@app.route('/comment', methods=['POST'])
@payment.required(500)
def comment():
    try:
        post_id = request.form['post_id']
        comment = request.form['comment']
        payee_username = request.form['username']
        success = db.insert_comment(post_id, comment, payee_username)
        if success:
            return(db.get_comment_list_string(post_id))
        else:
            return('No post with index of %s' % (str(post_id)))
    except Exception as e:
        print(e)


@app.route('/upvoteComment', methods=['POST'])
@payment.required(50)
def upvote_comment():
    try:
        post_id = request.form['post_id']
        comment_id = request.form['comment_id']
        success, payee_username = db.upvote_comment(post_id, comment_id)
        if success:
            pay(payee_username, 50)
            return(db.get_comment_list_string(post_id))
        else:
            return('Comment with Post ID: %s and Comment Id: %s' %
                   (str(post_id), str(comment_id)))
    except Exception as e:
        print(e)


@app.route('/downvoteComment', methods=['POST'])
@payment.required(50)
def downvote_comment():
    post_id = request.form['post_id']
    comment_id = request.form['comment_id']
    success = db.downvote_comment(post_id, comment_id)
    if success:
        return(db.get_comment_list_string(post_id))
    else:
        return('Comment with Post ID: %s and Comment Id: %s' %
               (str(post_id), str(comment_id)))


@app.route('/')
def home():
    links = db.get_post_list()
    links = [dict(post_id=link[0], url=link[1], user=link[2], votes=link[3],
             title=link[4], image=link[5], time=link[6]) for link in links]
    return(render_template('home.html', links=links))


@app.route('/comments')
def comments():
    try:
        post_id = int(request.args.get('postId'))
        comments = db.get_comment_list(post_id)
        comments = [dict(comment_id=comment[1], user=comment[3],
                    text=comment[2], votes=comment[4], time=comment[5])
                    for comment in comments]
        link = db.get_link(post_id)
        link = dict(post_id=link[0], url=link[1], user=link[2], votes=link[3],
                    title=link[4], image=link[5], time=link[6])
        return(render_template('comments.html', comments=comments, link=link))
    except Exception as e:
        print(e)


@app.route('/about')
def about():
    return render_template('about.html')


@app.template_filter('timesince')
def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """

    now = datetime.datetime.utcnow()
    diff = now - datetime.datetime.strptime(dt,  "%Y-%m-%d %H:%M:%S.%f")

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )
    for period, singular, plural in periods:

        if period >= 1:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


def pay(payee_username, price):
    bit_transfer = json.dumps({
        'payer': username,
        'payee_username': payee_username,
        'amount': price,
        'timestamp': time.time(),
        'description': 'Test On Chain'
    })
    signature = wallet.sign_message(bit_transfer)
    verification_url = BitTransfer.verification_url.format(payee_username)

    return requests.post(verification_url,
                         data=json.dumps({'bittransfer': bit_transfer,
                                          'signature': signature}),
                         headers={'content-type': 'application/json'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')

