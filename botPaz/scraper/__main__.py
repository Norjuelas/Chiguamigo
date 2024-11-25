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
        #USER_PASSWORD=os.getenv('GCP_PROJECT_ID')
        USER_NAME= os.getenv('TWITTER_USERNAME')
        USER_PASSWORD=os.getenv('TWITTER_PASSWORD')

        os.getenv('GCP_PROJECT_ID')
        if USER_NAME is not None and USER_PASSWORD is not None:
            scraper = TwitterAgent(
                mail="",
                username=USER_NAME,
                password=USER_PASSWORD,
            )
            scraper.login()
            #Logica para segmentar targets  
            #scraper.scrape_tweets(
            #    max_tweets=10, 
            #    #no_tweets_limit= args.no_tweets_limit if args.no_tweets_limit is not None else True,
            #    scrape_username= "PauPathway"
                #scrape_hashtag=args.hashtag,
                #scrape_query=args.query,
                #scrape_latest=args.latest,
                #scrape_top=args.top,
                #scrape_poster_details="pd" in additional_data,
            #)
            scraper.reply("esto lo hice desde un bot :B",1860124831104311649,"https://x.com/PauPathway/status/1860124831104311649")
            if not scraper.interrupted:
                scraper.driver.close()
        else:
            print(
                "Missing Twitter username or password environment variables. Please check your .env file."
            )
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(1)


if __name__ == "__main__":
    main()