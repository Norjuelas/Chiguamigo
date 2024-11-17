from selenium.webdriver import WebDriver
from typing import List, Dict, Any, Optional
import logging
from .browser import Browser
from "../../constants" import TIMEOUTS

class User:
    """
    A class to interact with Twitter user profiles using Selenium WebDriver.
    """
    
    def __init__(self, driver: WebDriver, username: str):
        """
        Initialize the User class.
        
        Args:
            driver: Selenium WebDriver instance
            username: Twitter username to interact with
        """
        self.driver = driver
        self.username = username
        self.on_user_page = False
        self.browser = Browser(self.driver)
        
    async def get_to_user(self) -> None:
        """Navigate to user's profile page if not already there."""
        if not self.on_user_page:
            await self.browser.go_to_page(
                f"https://twitter.com/{self.username}",
                "css",
                "[alt='Opens profile photo']",
                TIMEOUTS.WAIT_FOR_ELEMENT
            )
            self.on_user_page = True

    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile information.
        
        Returns:
            Dictionary containing user profile details or None if failed
        """
        try:
            await self.get_to_user()
            await self.browser.sleep_default()

            scrap_user_script = f"""
                function processNum(n) {{
                    if (!n) return null;
                    
                    if (n.includes('K')) {{
                        n = n.replace('K', '').replace(',', '');
                        return parseFloat(n) * 1000;
                    }}
                    
                    if (n.includes('M')) {{
                        n = n.replace('M', '').replace(',', '');
                        return parseFloat(n) * 1000000;
                    }}
                    
                    return parseFloat(n.replace(',', ''));
                }}

                let userNameRaw = document.querySelector('[data-testid="UserName"]')
                                .innerText.split(String.fromCharCode(0x0a));
                
                let following = document.querySelector('[href="/{self.username}/following"]')?.innerText.split(" ")[0];
                let followers = document.querySelector('[href="/{self.username}/followers"]')?.innerText.split(" ")[0];

                return {{
                    'display_name': userNameRaw[0],
                    'username': userNameRaw[1],
                    'bio': document.querySelector('[data-testid="UserDescription"]')?.innerText || null,
                    'location': document.querySelector('[data-testid="UserLocation"]')?.innerText || null,
                    'url': window.location.href,
                    'professional_category': document.querySelector('[data-testid="UserProfessionalCategory"]')?.innerText || null,
                    'following_count': processNum(following),
                    'followers_count': processNum(followers),
                    'profile_photo': document.querySelector('[alt="Opens profile photo"]')?.src || null
                }};
            """

            return await self.browser.sync_execute_js(scrap_user_script)
            
        except Exception as e:
            logging.error(f"Error fetching user info for @{self.username}: {str(e)}")
            return None

    async def get_followers(self, limit: int) -> List[str]:
        """
        Get list of user's followers.
        
        Args:
            limit: Maximum number of followers to fetch
            
        Returns:
            List of follower usernames
        """
        await self.browser.go_to_page(
            f"https://twitter.com/{self.username}/followers",
            "css",
            "[data-testid='UserCell']"
        )

        final_following = []
        
        while len(final_following) < limit:
            try:
                scrapped_following = await self.browser.sync_execute_js("""
                    const followers = document.querySelectorAll("[data-testid='UserCell']");
                    return Array.from(followers).map(user => 
                        user.querySelector("a").href.split("/")[3]
                    );
                """)

                final_following = list(set(final_following + scrapped_following))
                
                await self.browser.scroll_page()
                await self.browser.wait_for_element("css", "[data-testid='UserCell']")
                
            except Exception as e:
                logging.error(f"Error scraping followers: {str(e)}")
                break

        return final_following[:limit]

    async def get_following(self, limit: int) -> List[str]:
        """
        Get list of users that this user follows.
        
        Args:
            limit: Maximum number of following to fetch
            
        Returns:
            List of following usernames
        """
        await self.browser.go_to_page(
            f"https://twitter.com/{self.username}/following",
            "css",
            "[data-testid='UserCell']"
        )

        final_following = []

        while len(final_following) < limit:
            try:
                scrapped_following = await self.browser.sync_execute_js("""
                    const following = document.querySelectorAll("[data-testid='UserCell']");
                    return Array.from(following).map(user => 
                        user.querySelector("a").href.split("/")[3]
                    );
                """)

                final_following = list(set(final_following + scrapped_following))

                await self.browser.scroll_page()
                await self.browser.wait_for_element("css", "[data-testid='UserCell']")
                await self.browser.sleep(1, 2)

                if await self.browser.finished_scrolling(97):
                    break

            except Exception as e:
                logging.error(f"Error scraping following: {str(e)}")
                break

        return final_following[:limit]

    async def unfollow(self) -> bool:
        """
        Unfollow this user.
        
        Returns:
            Boolean indicating if unfollow was successful
        """
        try:
            await self.get_to_user()
            await self.browser.sleep_default()

            unfollow_button = await self.browser.sync_execute_js(
                'return document.querySelector("[data-testid$=\'-unfollow\']")'
            )

            if unfollow_button:
                await self.browser.sync_execute_js(
                    'document.querySelector("[data-testid$=\'-unfollow\']").click()'
                )
                await self.browser.sleep_default()
                await self.browser.sync_execute_js(
                    'document.querySelector("[data-testid=\'confirmationSheetConfirm\']").click()'
                )
                logging.info(f"Successfully unfollowed @{self.username}")
                return True
                
            logging.info(f"No unfollow button found for @{self.username}")
            return False
            
        except Exception as e:
            logging.error(f"Error unfollowing @{self.username}: {str(e)}")
            return False

    async def follow(self) -> bool:
        """
        Follow this user.
        
        Returns:
            Boolean indicating if follow was successful
        """
        try:
            await self.get_to_user()
            await self.browser.sleep_default()

            follow_button = await self.browser.sync_execute_js(
                'return document.querySelector("[data-testid$=\'-follow\']")'
            )

            if follow_button:
                await self.browser.sync_execute_js(
                    'document.querySelector("[data-testid$=\'-follow\']").click()'
                )
                await self.browser.sleep_default()
                logging.info(f"Successfully followed @{self.username}")
                return True
                
            logging.info(f"No follow button found for @{self.username}")
            return False
            
        except Exception as e:
            logging.error(f"Error following @{self.username}: {str(e)}")
            return False