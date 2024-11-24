import os
import sys
import argparse
from twitter_agent import TwitterAgent

try:
    from dotenv import load_dotenv

    print("Loading .env file")
    load_dotenv()
    print("Loaded .env file\n")
except Exception as e:
    print(f"Error loading .env file: {e}")
    sys.exit(1)


def main():
    try:
        parser = argparse.ArgumentParser(
            add_help=True,
            usage="python scraper [option] ... [arg] ...",
            description="Twitter Scraper is a tool that allows you to scrape tweets from Twitter without using Twitter's API.",
        )

        # Argumentos generales
        parser.add_argument(
            "-t",
            "--tweets",
            type=int,
            default=50,
            help="Number of tweets to scrape (default: 50)",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=None,
            help="Twitter username. Scrape tweets from a user's profile.",
        )
        parser.add_argument(
            "-ht",
            "--hashtag",
            type=str,
            default=None,
            help="Twitter hashtag. Scrape tweets from a hashtag.",
        )
        parser.add_argument(
            "-ntl",
            "--no_tweets_limit",
            nargs='?',
            default=False,
            help="Set no limit to the number of tweets to scrape (will scrape until no more tweets are available).",
        )
        parser.add_argument(
            "-q",
            "--query",
            type=str,
            default=None,
            help="Twitter query or search. Scrape tweets from a query or search.",
        )
        parser.add_argument(
            "-a",
            "--add",
            type=str,
            default="",
            help="Additional data to scrape and save in the .csv file.",
        )
        parser.add_argument(
            "--latest",
            action="store_true",
            help="Scrape latest tweets",
        )
        parser.add_argument(
            "--top",
            action="store_true",
            help="Scrape top tweets",
        )

        args = parser.parse_args()

        # Recuperar credenciales de entorno
        USER_MAIL = os.getenv("TWITTER_MAIL")
        USER_UNAME = os.getenv("TWITTER_USERNAME")
        USER_PASSWORD = os.getenv("TWITTER_PASSWORD")

        if not USER_UNAME or not USER_PASSWORD:
            print("Error: Missing Twitter username or password in environment variables.")
            print("Ensure your .env file contains TWITTER_USERNAME and TWITTER_PASSWORD.")
            sys.exit(1)

        # Validación de argumentos de tipo de scraping
        tweet_type_args = []
        if args.username:
            tweet_type_args.append(args.username)
        if args.hashtag:
            tweet_type_args.append(args.hashtag)
        if args.query:
            tweet_type_args.append(args.query)

        if len(tweet_type_args) > 1:
            print("Please specify only one of --username, --hashtag, or --query.")
            sys.exit(1)

        if args.latest and args.top:
            print("Please specify either --latest or --top. Not both.")
            sys.exit(1)

        # Datos adicionales
        additional_data: list = args.add.split(",")

        # Iniciar el scraper
        scraper = TwitterAgent(
            mail=USER_MAIL,
            username=USER_UNAME,
            password=USER_PASSWORD,
        )
        scraper.login()
        scraper.scrape_tweets(
            max_tweets=args.tweets,
            no_tweets_limit=args.no_tweets_limit if args.no_tweets_limit is not None else True,
            scrape_username=args.username,
            scrape_hashtag=args.hashtag,
            scrape_query=args.query,
            scrape_latest=args.latest,
            scrape_top=args.top,
            scrape_poster_details="pd" in additional_data,
        )
        scraper.save_to_csv()
        if not scraper.interrupted:
            scraper.driver.close()

    except KeyboardInterrupt:
        print("\nScript Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(1)


if __name__ == "__main__":
    main()
