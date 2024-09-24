from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from rich import print

def check_and_skip_ad(driver):
    try:
        # Check if the ad preview image is present
        ad_preview = driver.find_element(By.CLASS_NAME, "ytp-preview-ad__image")
        
        if ad_preview:
            # Wait for the skip button to become visible and clickable
            skip_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ytp-skip-ad-button"))
            )
            
            # Wait for the button to become visible (style doesn't contain "display: none;")
            WebDriverWait(driver, 30).until(
                lambda d: "display: none;" not in d.find_element(By.CLASS_NAME, "ytp-skip-ad-button").get_attribute("style")
            )
            
            # Click the skip button
            skip_button.click()
            print("[LOG] [bold yellow]Ad skipped successfully![/bold yellow]")
    except NoSuchElementException:
        # Ad not found, silently continue
        print("[LOG] 📦 [bold green]No ads found[/bold green]")
        pass

    except Exception as e:
        print(f"No ad found or error occurred: {str(e)}")
    
    return driver