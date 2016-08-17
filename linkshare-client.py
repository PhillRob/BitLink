import json
import requests
import click

from two1.commands.config import Config
from two1.wallet import Wallet
from two1.bitrequests import BitTransferRequests

wallet = Wallet()
username = Config().username
bit_requests = BitTransferRequests(wallet, username)

server_url = 'http://70.174.36.208:8000/'


@click.group()
def main():
    """cli for link-share"""


@click.command()
@click.argument('link')
@click.option('--title', default='')
@click.option('--image', default=('http://www.bbb.org/blog/wp-content/uploads/'
              '2013/05/bitcoin1.png'))
def add_link(link, title, image):
    try:
        test_valid = requests.get(link)
        if title == '':
            title = link
        res = bit_requests.post(url=server_url+'add',
                                data={
                                      'url': link,
                                      'username': username,
                                      'title': title,
                                      'image': image
                                      })
        print(res.text)
    except Exception:
        print('Invalid URL')


@click.command()
@click.argument('post_id')
def upvote(post_id):
    res = bit_requests.post(url=server_url+'upvote', data={'post_id': post_id})
    print(res.text)


@click.command()
@click.argument('post_id')
def downvote(post_id):
    res = bit_requests.post(url=server_url+'downvote',
                            data={'post_id': post_id})
    print(res.text)


@click.command()
@click.argument('post_id')
@click.argument('text', nargs=-1)
def comment(post_id, text):
    comment = ""
    for word in text:
        comment += word + " "
    res = bit_requests.post(url=server_url+'comment',
                            data={
                                'post_id': post_id,
                                'comment': comment,
                                'username': username
                            })
    print(res.text)


@click.command()
@click.argument('post_id')
@click.argument('comment_id')
def upvote_comment(post_id, comment_id):
    res = bit_requests.post(url=server_url+'upvoteComment',
                            data={
                                  'post_id': post_id,
                                  'comment_id': comment_id
                                  })
    print(res.text)


@click.command()
@click.argument('post_id')
@click.argument('comment_id')
def downvote_comment(post_id, comment_id):
    res = bit_requests.post(url=server_url+'downvoteComment',
                            data={
                                  'post_id': post_id,
                                  'comment_id': comment_id
                                  })
    print(res.text)

main.add_command(add_link)
main.add_command(upvote)
main.add_command(downvote)
main.add_command(comment)
main.add_command(upvote_comment)
main.add_command(downvote_comment)

if __name__ == "__main__":
    main()
