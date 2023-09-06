from peewee import Model, CharField, DateTimeField, BooleanField, IntegerField, UUIDField
from database import db


class BilibiliAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    title = CharField()
    is_verified = BooleanField()
    profile_image_url = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'bilibili_accounts'


class InstagramAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    username = CharField()
    title = CharField()
    is_verified = BooleanField()
    profile_image_url = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'instagram_accounts'


class TikTokAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    username = CharField(unique=True)
    title = CharField()
    is_verified = BooleanField()
    profile_image_url = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'tiktok_accounts'


class TwitchAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    username = CharField(unique=True)
    title = CharField()
    profile_image_url = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'twitch_accounts'


class TwitterAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    username = CharField(unique=True)
    title = CharField()
    is_verified = BooleanField()
    profile_image_url = CharField(null=True)
    banner_image_url = CharField(null=True)
    is_sensitive = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'twitter_accounts'


class YouTubeAccount(Model):
    id = UUIDField(index=True, primary_key=True)
    account_id = CharField(unique=True)
    username = CharField(unique=True)
    title = CharField()
    badge = CharField(null=True)  # Store the badge type as a string
    is_membership_enabled = BooleanField()
    profile_image_url = CharField(null=True)
    banner_image_url = CharField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'youtube_accounts'
