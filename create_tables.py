from database import connect_db
from account_models import *
from metric_models import *


db = connect_db()
db.create_tables([
    BilibiliAccount,
    InstagramAccount,
    TikTokAccount,
    TwitchAccount,
    TwitterAccount,
    YouTubeAccount,
    BilibiliMetric,
    InstagramMetric,
    TikTokMetric,
    TwitchMetric,
    TwitterMetric,
    YouTubeMetric
])
