import asyncio
import logging
from typing import List
from src.classes.crow.twitter_client import TwitterClient
from src.classes.crow.user import User

async def unfollow_users(driver, target_username: str, limit: int = 326):
    """
    Unfollows users from a target account.
    
    Args:
        driver: Selenium WebDriver instance
        target_username (str): Username to unfollow from
        limit (int): Maximum number of users to unfollow
    """
    try:
        # Create user instance for target account
        user = User(driver, target_username)
        
        # Get list of users to unfollow
        users_to_unfollow: List[str] = await user.get_following(limit)
        logging.info(f"Found {len(users_to_unfollow)} users to unfollow")
        
        # Unfollow each user
        for index, username in enumerate(users_to_unfollow, 1):
            try:
                current_user = User(driver, username)
                await current_user.unfollow()
                logging.info(f"[{index}/{len(users_to_unfollow)}] Unfollowed @{username}")
                
                # Optional: Add a small delay between unfollows to avoid rate limits
                await asyncio.sleep(2)
                
            except Exception as e:
                logging.error(f"Failed to unfollow @{username}: {str(e)}")

    except Exception as e:
        logging.error(f"Error during unfollow process: {str(e)}")
        raise

async def main():
    """
    Main function to initialize the Twitter client and start the unfollow process.
    """
    try:
        # Initialize the Twitter client
        client = TwitterClient()
        driver = await client.get_client()
        
        if driver:
            # Start unfollow process
            await unfollow_users(
                driver=driver,
                target_username="takucoder",
                limit=326
            )
        else:
            logging.error("Failed to initialize Twitter client")
            
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
    finally:
        # Ensure we close the driver properly
        if 'client' in locals() and hasattr(client, 'driver'):
            client.driver.quit()
            logging.info("Browser session closed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run the async main function
    asyncio.run(main())