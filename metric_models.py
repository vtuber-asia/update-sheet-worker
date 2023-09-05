from peewee import Model, CharField, DateTimeField, IntegerField, UUIDField
from database import db


class BilibiliMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    followers_count = IntegerField()
    followings_count = IntegerField()
    likes_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'bilibili_metrics'


class InstagramMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    followers_count = IntegerField()
    followings_count = IntegerField()
    posts_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'instagram_metrics'


class TikTokMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    followers_count = IntegerField()
    followings_count = IntegerField()
    likes_count = IntegerField()
    videos_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'tiktok_metrics'


class TwitchMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    followers_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'twitch_metrics'


class TwitterMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    followers_count = IntegerField()
    followings_count = IntegerField()
    medias_count = IntegerField()
    tweets_count = IntegerField()
    favorites_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'twitter_metrics'


class YouTubeMetric(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField()
    subscribers_count = IntegerField()
    videos_count = IntegerField()
    views_count = IntegerField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'youtube_metrics'
