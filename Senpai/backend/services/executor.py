from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Dict, Any, List
import logging
import asyncio
from selenium.webdriver.remote.webdriver import WebDriver
from backend.services import recorder
import time

class Executor:
    logger = logging.getLogger(__name__)
    selenium_grid_url: str = "http://localhost:5555/wd/hub"  # Replace with the actual Selenium Grid URL
    MAX_RETRIES: int = 3 # Maximum number of retries
    RETRY_DELAY: int = 2 # Delay between retries in seconds

    @classmethod
    def initialize(cls) -> None:
        """Initializes the Executor class."""
        cls.logger.info("Executor service initialized.")
        pass

    @classmethod
    async def get_browser_session(cls) -> WebDriver:
        """Connects to a Selenium Grid and returns a WebDriver instance."""
        try:
            # Connect to the Selenium Grid
            driver: WebDriver = webdriver.Remote(
                command_executor=cls.selenium_grid_url,
                desired_capabilities=webdriver.DesiredCapabilities.CHROME
            )
            cls.logger.info(f"Connected to Selenium Grid at {cls.selenium_grid_url}")
            return driver
        except Exception as e:
            cls.logger.exception(f"Error connecting to Selenium Grid")
            raise Exception(f"Error connecting to Selenium Grid: {e}")

    @classmethod
    async def execute_action(cls, browser_session: WebDriver, action: Dict[str, Any], dom: str, screenshot: bytes) -> None:
        """Executes a single recorded action with retries."""
        retries: int = 0
        while retries <= cls.MAX_RETRIES:
            try:
                action_type: str = action["type"]
                if action_type == "navigate":
                    url: str = action["url"]
                    browser_session.get(url)
                    cls.logger.info(f"Navigated to {url}")
                elif action_type == "click":
                    selector: str = action["selector"]
                    await cls._click_element(browser_session, selector, dom, screenshot)
                    cls.logger.info(f"Clicked element with selector '{selector}'")
                elif action_type == "enter_text":
                    selector: str = action["selector"]
                    text: str = action["value"]
                    await cls._enter_text(browser_session, selector, text, dom, screenshot)
                    cls.logger.info(f"Entered text '{text}' into selector '{selector}'")
                else:
                    cls.logger.warning(f"Unknown action type: {action_type}")
                # If successful, break out of the retry loop
                break
            except Exception as e:
                cls.logger.exception(f"Error executing action, attempt {retries + 1}: {action}")
                if retries == cls.MAX_RETRIES:
                    cls.logger.error(f"Max retries reached for action: {action}")
                    raise  # Re-raise the exception
                retries += 1
                await asyncio.sleep(cls.RETRY_DELAY) # Wait before retrying
        cls.logger.info(f"Successfully executed action: {action}")

    @classmethod
    async def execute_step(cls, browser_session: WebDriver, step: str, dom: str, screenshot: bytes) -> Dict[str, str]:
        """Executes a single step in the plan."""
        retries: int = 0
        log_data : Dict[str, str] = {}
        while retries <= cls.MAX_RETRIES:
            try:
                cls.logger.info(f"Executing step: {step}")
                # Implement logic to parse the step and perform the corresponding action in the browser
                # This is a placeholder implementation
                if "navigate to" in step.lower():
                    url:str = step.split("navigate to")[-1].strip()
                    browser_session.get(url)
                    cls.logger.info(f"Navigated to {url}")
                    log_data["action"] = f"Navigated to {url}"
                elif "click" in step.lower():
                    element_text: str = step.split("click")[-1].strip()
                    log_data["action"] = f"Click {element_text}"
                    await cls._click_element_by_text(browser_session, element_text, dom, screenshot)
                    cls.logger.info(f"Clicked element with text '{element_text}'")
                elif "enter" in step.lower():
                    parts: List[str] = step.split("enter")[-1].strip().split(" in ")

                    text_to_enter: str = parts[0]
                    selector: str = parts[1]
                    log_data["action"] = f"Enter {text_to_enter} in {selector}"
                    await cls._enter_text(browser_session, selector, text_to_enter, dom, screenshot)
                    cls.logger.info(f"Entered text '{text_to_enter}' into selector '{selector}'")
                else:
                    cls.logger.warning(f"Unknown step type: {step}")
                break # If successful break retry loop
            except Exception as e:
                cls.logger.exception(f"Error executing step, attempt {retries + 1}: {step}")
                if retries == cls.MAX_RETRIES:
                    cls.logger.error(f"Max retries reached for step: {step}")
                    raise  # Re-raise the exception
                retries += 1
                await asyncio.sleep(cls.RETRY_DELAY)  # Wait before retrying
        return log_data

    @classmethod
    async def execute_task_template(cls, browser_session: WebDriver, template_name: str="default_template.json", dom: str, screenshot: bytes):
        """Executes all actions from a template."""
        actions = recorder.Recorder.load_task_template(template_name)
        if not actions:
            cls.logger.warning(f"No actions found in template: {template_name}")
            return

        for action in actions:
            try:
                await cls.execute_action(browser_session, action, dom, screenshot)
            except Exception as e:
                cls.logger.error(f"Error during execute_task_template")
                return

    @classmethod
    async def _click_element_by_text(cls, browser_session: WebDriver, element_text: str, dom: str, screenshot: bytes, timeout: int = 10) -> None:
        """Clicks an element by its text content."""
        try:
            # First try to find the element by text content
            elements: List[Any] = browser_session.find_elements(By.XPATH, f"//*[contains(text(), '{element_text}')]" )
            if not elements:
                raise Exception(f"Could not find element with text '{element_text}'")

            element = elements[0]
            WebDriverWait(browser_session, timeout).until(
                EC.element_to_be_clickable(element)
            ).click()
            cls.logger.debug(f"Successfully clicked element with text: {element_text}")
        except Exception as e:
             cls.logger.error(f"Could not click element with text '{element_text}': {e}")
             raise Exception(f"Could not click element with text '{element_text}': {e}")

    @classmethod
    async def _click_element(cls, browser_session: WebDriver, selector: str, dom: str, screenshot: bytes, timeout: int = 10) -> None:
        """Clicks an element by its selector."""
        try:
            element = WebDriverWait(browser_session, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            cls.logger.debug(f"Successfully clicked element with selector: {selector}")
        except Exception as e:
             cls.logger.error(f"Could not click element with selector '{selector}': {e}")
             raise Exception(f"Could not click element with selector '{selector}': {e}")

    @classmethod
    async def _enter_text(cls, browser_session: WebDriver, selector: str, text: str, dom: str, screenshot: bytes, timeout: int = 10) -> None:
        """Enters text into an element identified by the selector."""
        try:
            element = WebDriverWait(browser_session, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()  # Clear existing text, if any
            element.send_keys(text)
            cls.logger.debug(f"Successfully entered text '{text}' into selector: {selector}")
        except Exception as e:
            cls.logger.error(f"Could not enter text '{text}' into selector '{selector}': {e}")
            raise Exception(f"Could not enter text '{text}' into selector '{selector}': {e}")
