import configparser
from collections import deque
from time import sleep
import tweepy

config = configparser.ConfigParser()
config.read('config.ini')

# You can provide the consumer key and secret with the access token and access
# token secret to authenticate as a user
client = tweepy.Client(
    consumer_key=config['TWITTER']['consumer_key'],
    consumer_secret=config['TWITTER']['consumer_secret'],
    access_token=config['TWITTER']['access_token'],
    access_token_secret=config['TWITTER']['access_token_secret'],
)

accounts = {}
display_tweets = deque([""]*5, maxlen=10)
max_id = 0

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = 0
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

while True:
    # Client.get_home_timeline(*, end_time=None, exclude=None, expansions=None, max_results=None, media_fields=None, pagination_token=None, place_fields=None, poll_fields=None, since_id=None, start_time=None, tweet_fields=None, until_id=None, user_fields=None, user_auth=True)
    response = client.get_home_timeline(
        max_results=10,
        since_id=max_id,
        tweet_fields=["entities", "source", "author_id", "attachments", "created_at", "geo"],
        expansions=['entities.mentions.username','author_id'],
        user_fields=['username'],
    )
    if len(response.includes.get('users',[])) > 0:
        for user in response.includes['users']:
            accounts[user.id] = user.username

    tweets = response.data
    print(f"Got {len(tweets) if tweets is not None else 0} Tweets")
    if tweets:
        for tweet in tweets:
            t = f"""@{accounts[tweet.author_id]} - {pretty_date(tweet.created_at)}
            {tweet.text} {tweet.attachments or ""}
            """
            if tweet.author_id == 1279816776289792000 and "timberlea" not in tweet.text.lower():
                continue
            display_tweets.appendleft(t)
            if tweet.id > max_id:
                max_id = tweet.id

    print(list(display_tweets))
    sleep(5)


#Next Verify format that might look good on home assistant
#--Not many options. Maybe log each tweet as event, then use log book card to show history of tweets.  No need for queue then.?