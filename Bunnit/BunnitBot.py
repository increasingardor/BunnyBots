from urllib.parse import quote_plus
import asyncio
import asyncpraw
import datetime
import requests
import json
import pprint
import dotenv
import os

async def main():
    # Load the local environment variables so we don't keep secrets in public view
    dotenv.load_dotenv(dotenv.find_dotenv())
    
    # Connects to Reddit
    reddit = asyncpraw.Reddit(
        CLIENT_ID = os.getenv("CLIENT_ID"),
        CLIENT_SECRET = os.getenv("CLIENT_SECRET"),
        user_agent="BunnitBot 1.1",
    )
    await connect(reddit)

async def connect(reddit):
    print("\n\n\tRunning BunnitBot 1.1\n\nSearching for Bunny...")
    bunny = await reddit.redditor(os.getenv("REDDITOR"))

    # Requests a stream of all of Bunny's posts from Reddit. Continues waiting for more posts.
    # As each new post comes in, it is processed.
    async for post in bunny.stream.submissions():
        await process_post(post)

async def process_post(post):
    # When the bot is restarted Reddit will resend it ALL posts for the specified Redditor, so we limit based on timestamp.
    # Opens and reads file storing timestamp of last post.
    log = open(os.getenv("LAST_UPDATED"), "r")
    last_date = log.readline()
    log.close()

    # Writes post.id to file; referenced in Disco for the !bunny command
    with open(os.getenv("POSTS"), "a") as file:
        file.write(f"{post.id}\n")

    # Only posts if the post's timestamp is later than the one on file.
    if datetime.datetime.utcfromtimestamp(float(last_date)) < datetime.datetime.utcfromtimestamp(post.created_utc):
        print(f"\nNew post found in {post.subreddit.display_name}! {datetime.datetime.today()}")
        await post_to_discord(post)
                
def get_image_url(post):
    # Parses url for the image to display in Discord.
    # Discord doesn't display Imgur's animated .gifv files at all, so we request the .jpg instead.
    if post.url.find("imgur") > -1:
        return post.url.replace("gifv", "jpg")

    # With timestamp exclusions, we probably don't need to worry about this, but just in case,
    # we pull a placeholder for posts removed by Reddit.
    elif post.title.find("Removed by Reddit") > -1:
        return "https://www.publicdomainpictures.net/pictures/280000/nahled/not-found-image-15383864787lu.jpg"

    # For Reddit galleries we grab the first image in the previews.
    elif post.url.find("gallery") > -1:
        for i in post.media_metadata.items():
            return i[1]["p"][0]["u"]

    # For one-image Reddit posts we grab the image URL.
    else:
        return post.preview["images"][0]["source"]["url"]
        
async def post_to_discord(post):
    image_url = get_image_url(post)
    reddit_channel = os.getenv("REDDIT_CHANNEL")
    main_channel = os.getenv("MAIN_CHANNEL")

    # Build the Discord webhook object.
    hook = {
        # An embed is a special Discord object that includes images, text and a special border.
        "embeds": [
            {
                "author": {
                    "name": f"{post.author.name}",
                    "url": f"http://reddit.com/u/{post.author.name}"
                },
                "title": post.title,
                "url": f"http://reddit.com{post.permalink}",
                "footer":
                    {
                        "text": f"Posted to {post.subreddit.display_name} • {datetime.date.today().strftime('%m/%d/%Y')}"
                    },
                "color": 14886454,
                "image": {
                    "url": image_url
                }
            }
        ]
    }
    await send_hook(reddit_channel, hook)
    await send_hook(main_channel, hook)

    # Write the new post timestamp to file.
    log = open(os.getenv("LAST_UPDATED"), "w")
    log.write(str(post.created_utc))
    log.close()

async def send_hook(url, payload):
    # Post the webhook object to Discord
    result = requests.post(url, json=payload)
    if 200 <= result.status_code < 300:
        print(f"Posted {datetime.datetime.today()}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
