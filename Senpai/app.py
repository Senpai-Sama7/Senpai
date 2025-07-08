from agent.browser_controller import BrowserController
from agent.planner import Planner
from agent.observer import Observer
import os

def main():
    # Configuration
    OPENAI_API_KEY = "your_openai_api_key"  # Replace with your key
    ZIP_CODE = "10001"
    SCREENSHOT_PATH = "static/screenshots/weather_summary.png"

    # Initialize components
    browser = BrowserController()
    planner = Planner(api_key=OPENAI_API_KEY)
    observer = Observer()

    # Task
    command = "check today’s weather on weather.com"
    print(f"Executing command: {command}")

    # 1. Navigate to weather.com
    browser.navigate_to("https://weather.com")

    # 2. Get DOM and generate plan (simplified for MVP)
    dom = browser.get_page_source()
    plan = [
        "Enter ZIP code '10001'",
        "Click on the 'Today' tab",
        "Take a screenshot of the summary"
    ]
    print("Plan:")
    for step in plan:
        print(f"- {step}")

    # 3. Execute plan
    print("
Execution Log:")
    try:
        # Enter ZIP code
        browser.enter_text("input#LocationSearch_input", ZIP_CODE)
        print("- Entered ZIP code")

        # Click search
        browser.click_element("button.Search--submit")
        print("- Clicked search")

        # Wait for and click 'Today' tab
        browser.click_element("a[data-testid='todaysForecast']")
        print("- Clicked 'Today' tab")

        # Take screenshot
        os.makedirs(os.path.dirname(SCREENSHOT_PATH), exist_ok=True)
        browser.take_screenshot(SCREENSHOT_PATH)
        print(f"- Screenshot saved to {SCREENSHOT_PATH}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close()
        print("
Done.")

if __name__ == "__main__":
    main()
