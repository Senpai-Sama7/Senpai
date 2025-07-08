import logging
import json
from selenium.webdriver.common.by import By
from typing import Dict, Any, List, Optional

class Recorder:
    logger = logging.getLogger(__name__)

    @classmethod
    def initialize(cls) -> None:
        """Initializes the Recorder class."""
        cls.logger.info("Recorder service initialized.")
        pass

    @classmethod
    def record_action(cls, browser_session: object, action_type: str, selector: Optional[str] = None, value: Optional[str] = None) -> Dict[str, Any]:
        """Records a user action."""
        action: Dict[str, Any] = {"type": action_type}
        if selector:
            # Generalize the selector
            generalized_selector: str = cls.generalize_selector(browser_session, selector)
            action["selector"] = generalized_selector
        if value:
            action["value"] = value
        cls.logger.info(f"Recorded action: {action}")
        return action

    @classmethod
    def generalize_selector(cls, browser_session: object, selector: str) -> str:
        """Generalizes the selector using different strategies."""
        try:
            element = browser_session.find_element(By.CSS_SELECTOR, selector)

            # 1. Try to use ID
            if element.get_attribute("id"):
                id_selector: str = f"#{element.get_attribute('id')}"
                try:
                    browser_session.find_element(By.CSS_SELECTOR, id_selector)  # Verify it's unique
                    cls.logger.info(f"Generalized selector to ID: {id_selector}")
                    return id_selector
                except:
                    pass

            # 2. Try to use XPath
            try:
                xpath: str = cls.get_xpath(browser_session, element)
                cls.logger.info(f"Generalized selector to XPath: {xpath}")
                return xpath
            except Exception:
                cls.logger.warning(f"Could not generalize selector to XPath")
                pass

            # 3. If all else fails, return the original selector
            return selector
        except Exception as e:
            cls.logger.exception("Error generalizing selector")
            return selector

    @classmethod
    def get_xpath(cls, browser_session: object, element: object) -> str:
         """Generates an XPath for the given element."""
         try:
             def javascript_test(element: object) -> str:
                 from selenium import webdriver  # noqa: F401
                 driver = element._parent
                 parts: List[str] = []
                 def traverse(element: object) -> str:
                     tag: str = element.tag_name.lower()
                     if tag == "html":
                         return '/html[1]'
                     ix: int = 1
                     sibs: List[object] = element.find_elements(By.XPATH, "./preceding-sibling::" + tag)
                     ix += len(sibs)
                     return traverse(element.find_element(By.XPATH, '..')) + "/" + tag + "[" + str(ix) + "]"
                 return traverse(element)
             return browser_session.execute_script(javascript_test, element)
         except Exception as e:
             return ""

    @classmethod
    def save_task_template(cls, actions: List[Dict[str, Any]], template_name: str = "default_template.json") -> bool:
        """Saves the recorded actions as a task template."""
        try:
            with open(template_name, "w") as f:
                json.dump(actions, f)
            cls.logger.info(f"Saved task template to {template_name}")
            return True
        except Exception as e:
            cls.logger.exception("Error saving task template")
            return False

    @classmethod
    def load_task_template(cls, template_name: str = "default_template.json") -> List[Dict[str, Any]]:
        """Loads a task template from a file."""
        try:
            with open(template_name, "r") as f:
                actions: List[Dict[str, Any]] = json.load(f)
            cls.logger.info(f"Loaded task template from {template_name}")
            return actions
        except FileNotFoundError:
            cls.logger.warning(f"Task template not found: {template_name}")
            return []
        except Exception as e:
            cls.logger.exception("Error loading task template")
            return []
