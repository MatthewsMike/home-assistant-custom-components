import configparser

import tweepy
import pprint
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
accounts[1279816776289792000] = "@HRFE_Incidents"
accounts[465512204] = "@HalifaxReTails"
accounts[90450219] = "@HfxRegPolice"
accounts[4159788513] = "@HRMFireNews"

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


# Client.get_home_timeline(*, end_time=None, exclude=None, expansions=None, max_results=None, media_fields=None, pagination_token=None, place_fields=None, poll_fields=None, since_id=None, start_time=None, tweet_fields=None, until_id=None, user_fields=None, user_auth=True)
response = client.get_home_timeline(
    max_results=10,
    tweet_fields=["entities", "source", "author_id", "attachments", "created_at", "geo"],
    expansions=['entities.mentions.username'],
    user_fields=['username'],
)

tweets = response.data
good_tweets = []
for tweet in tweets:
    t = f"""{accounts[tweet.author_id]} - {pretty_date(tweet.created_at)}
    {tweet.text} {tweet.attachments or ""}
    """
    if tweet.author_id == 1279816776289792000 and "timberlea" not in tweet.text.lower():
        continue
    good_tweets.append(t)


for t in good_tweets:
    print(t + "\n")


#Next Verify format that might look good on home assistant
#Dynamically populate Author table if key not found
#Cache checking time to on get newer tweets
#Cache tweets to display and keep a rolling buffer of 5? newest tweets