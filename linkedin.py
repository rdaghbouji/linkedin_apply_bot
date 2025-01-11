import time
import random
import utils
import constants
import openai

from utils import setup_driver, generate_urls, get_job_properties, retry_find_element, retry_find_elements, save_screenshot_with_path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def easy_apply_button(driver):
    try:
        button = retry_find_element(driver,By.XPATH, "//body//div//div[contains(@role,'main')]//div//div//div//div//div//div//div//div//span[1]")
        return button if button.is_displayed() else False
    except Exception:
        return False

def display_write_results(line_to_write):
    """Print and log results of each application attempt."""
    try:
        print(line_to_write)
        utils.writeResults(line_to_write)
    except Exception as e:
        utils.prRed(f"Error in display_write_results: {e}")

#######################################################################################################################################

def apply_for_job(driver, offer_page, job_properties):
    """
    Main function to handle the application workflow based on the defined steps.
    """
    # Step 2: Handle resume choice
    if not resume_choice(driver):
        display_write_results(f"{job_properties} | * 🥵 Failed at resume choice: {offer_page}")
        return

    # Step 3: Handle additional questions (if any)
    if handle_additional_questions(driver):
        print("Handled additional questions successfully.")
    else:
        print("No additional questions or failed at additional questions step.")

    # Step 4: Submit application
    if submit_application(driver):
        display_write_results(f"{job_properties} | * 🥳 Successfully applied to the job: {offer_page}")
    else:
        display_write_results(f"{job_properties} | * 🥵 Could not submit application for the job: {offer_page}")




def handle_continue_button(driver):
    """
    Helper function to locate and click the 'Next' button, using multiple methods to ensure accuracy.
    """
    try:
        # Attempt to find 'Next' button by ID and class, then XPath if needed
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id^='ember'] span.artdeco-button__text"))
            )
            next_button.click()
            print("Next button clicked successfully.")
            return True
        except (NoSuchElementException, TimeoutException):
            print("Next button by CSS selector not found. Trying XPath...")

        # XPath alternative
        try:
            next_button_xpath = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//span[@class='artdeco-button__text' and text()='Next'])[1]"))
            )
            next_button_xpath.click()
            print("Next button clicked successfully using XPath.")
            return True
        except (NoSuchElementException, TimeoutException):
            print("Next button by XPath not found.")
            return False

    except Exception as e:
        print(f"Error clicking Next button: {e}")
        save_screenshot_with_path(driver, "next_button_error.png")
        return False



def resume_choice(driver):
    """
    Handle resume choice step: press 'Next' or 'Review application'.
    """
    try:
        if handle_continue_button(driver):
            print("Proceeding to additional questions or review.")
            time.sleep(random.uniform(1, constants.botSpeed))
            return True
        elif handle_review_button(driver):
            print("Proceeding to review application step.")
            time.sleep(random.uniform(1, constants.botSpeed))
            return True
        else:
            print("Next or review button not found at resume choice step.")
            return False
    except Exception as e:
        print(f"Error during resume choice step: {e}")
        save_screenshot_with_path(driver, "resume_choice_error.png")
        return False


def handle_additional_questions(driver):
    """
    Handle additional questions: answer text input questions and intelligently select dropdown options.
    """
    try:
        while True:
            # Extract and fill in text input fields
            questions_and_boxes = extract_questions_and_input_boxes(driver)
            if questions_and_boxes:
                questions = [qa['question'] for qa in questions_and_boxes]
                responses = generate_responses(questions)
                fill_input_boxes(driver, questions_and_boxes, responses)

            # Handle dropdowns on the same page using OpenAI API for option selection
            dropdowns = extract_dropdowns(driver)
            if dropdowns:
                for dropdown in dropdowns:
                    try:
                        question_text = dropdown['question']
                        select = Select(dropdown['dropdown_box'])
                        options = [option.text.strip() for option in select.options]  # Normalize options

                        # Use OpenAI API to determine the best choice
                        selected_option = generate_dropdown_response(question_text, options).strip()
                        if selected_option in options:
                            select.select_by_visible_text(selected_option)
                            print(f"Dropdown for '{question_text}' selected with option: '{selected_option}'.")
                        else:
                            print(f"Generated response '{selected_option}' not found in dropdown options for '{question_text}'.")

                    except Exception as e:
                        print(f"Error selecting dropdown for '{dropdown['question']}': {e}")
                        save_screenshot_with_path(driver, "dropdown_error.png")

            # Move to the next page or press review
            if handle_continue_button(driver):
                print("Moving to the next page of additional questions.")
                time.sleep(random.uniform(1, constants.botSpeed))
            elif handle_review_button(driver):
                print("Reached the review step after additional questions.")
                time.sleep(random.uniform(1, constants.botSpeed))
                return True
            else:
                print("Neither 'Next' nor 'Review' button found at additional questions step.")
                return False
    except Exception as e:
        print(f"Error during additional questions handling: {e}")
        save_screenshot_with_path(driver, "additional_questions_error.png")
        return False

def generate_dropdown_response(question_text, options):
    """
    Use OpenAI API to generate a suitable response for a dropdown question based on its options.
    """
    prompt = f"Given the question: '{question_text}', choose the most appropriate response from these options: {options}. Provide only the best matching option text."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant trained to select the best answer from given options."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0  # Set low to encourage consistent output
        )
        # Extract the response and strip any leading/trailing whitespace
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating dropdown response: {e}")
        return options[0]  # Fallback to the first option if API call fails


def extract_questions_and_input_boxes(driver):
    """Extracts additional question text fields and their corresponding input boxes."""
    questions_and_boxes = []
    try:
        questions = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--label")  # Adjusted selector for labels
        input_boxes = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")  # Adjusted selector for input fields
        if len(questions) == len(input_boxes):
            questions_and_boxes = [{'question': question.text, 'input_box': input_box} for question, input_box in zip(questions, input_boxes)]
    except Exception as e:
        print(f"Error extracting questions and input boxes: {e}")
    return questions_and_boxes

def extract_dropdowns(driver):
    """Extracts dropdown questions and their corresponding select elements by linking labels to dropdowns."""
    dropdowns = []
    try:
        # Find all label elements for dropdowns
        labels = driver.find_elements(By.CSS_SELECTOR, "label.fb-dash-form-element__label")
        
        for label in labels:
            question_text = label.text.strip()
            dropdown_id = label.get_attribute("for")  # Get the 'for' attribute linking to the <select> element
            
            if dropdown_id:
                # Use the 'for' attribute to find the corresponding <select> element
                try:
                    dropdown_box = driver.find_element(By.ID, dropdown_id)
                    if dropdown_box.tag_name == "select":  # Ensure it's a <select> element
                        dropdowns.append({
                            'question': question_text,
                            'dropdown_box': dropdown_box
                        })
                        print(f"Found dropdown for question: '{question_text}'")
                except NoSuchElementException:
                    print(f"No dropdown found for label '{question_text}' with ID '{dropdown_id}'")
    except Exception as e:
        print(f"Error extracting dropdowns: {e}")
    return dropdowns


def submit_application(driver):
    """
    Submit the application by pressing the submit button.
    """
    try:
        # First try to locate the submit button by CSS selector and aria-label, then by XPath with the button text.
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']"))
            )
            submit_button.click()
            print("Submit button clicked successfully.")
            return True
        except (NoSuchElementException, TimeoutException):
            print("Submit button with aria-label not found. Trying alternative locators...")

        # Alternative approach using XPath with text 'Submit application'
        try:
            submit_button_xpath = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Submit application']"))
            )
            submit_button_xpath.click()
            print("Submit button clicked successfully using XPath.")
            return True
        except (NoSuchElementException, TimeoutException):
            print("Submit button by XPath not found.")

    except StaleElementReferenceException:
        print("Submit button became stale.")
    except Exception as e:
        print(f"An error occurred while submitting the application: {e}")
        save_screenshot_with_path(driver, "submit_application_error.png")
    return False



def handle_continue_button(driver, retries=3, delay=1):
    """
    Attempt to locate and click the 'Next' button by class name and other filters.
    Retry if a StaleElementReferenceException occurs or if the element is not found.
    """
    for attempt in range(retries):
        try:
            # Locate all elements with class name 'artdeco-button__text'
            buttons = driver.find_elements(By.CLASS_NAME, "artdeco-button__text")
            for button in buttons:
                # Check if the button text is 'Next'
                if button.text.strip() == "Next" and button.is_displayed():
                    button.click()
                    print("Next button clicked successfully.")
                    return True
            print(f"Attempt {attempt + 1} failed: 'Next' button not found or not clickable.")
            time.sleep(delay)
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Attempt {attempt + 1} for locating 'Next' button failed: {e}")
            time.sleep(delay)
    print("Next button could not be found or clicked after retries.")
    return False


def handle_review_button(driver):
    """
    Helper function to locate and click the 'Review application' button.
    """
    try:
        # Try locating the button using the ID and span with text 'Review'
        try:
            review_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id^='ember'] span.artdeco-button__text"))
            )
            if review_button.text.strip() == "Review":
                review_button.click()
                print("Review application button clicked successfully.")
                return True
        except (NoSuchElementException, TimeoutException):
            print("Review button with CSS selector 'button[id^=ember]' not found. Trying alternative locators...")

        # Fallback to XPath using the text 'Review'
        try:
            review_button_xpath = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Review']"))
            )
            review_button_xpath.click()
            print("Review application button clicked successfully using XPath.")
            return True
        except (NoSuchElementException, TimeoutException):
            print("Review button by XPath not found.")

    except StaleElementReferenceException:
        print("Review application button became stale.")
    except Exception as e:
        print(f"Error clicking Review button: {e}")
        save_screenshot_with_path(driver, "review_button_error.png")
    return False



def fill_input_boxes(driver, questions_and_boxes, responses):
    """Fill in the input boxes with responses to the questions."""
    for qa, response in zip(questions_and_boxes, responses):
        input_box = qa['input_box']
        input_box.clear()
        input_box.send_keys(response)


def generate_responses(questions):
    """Generate responses for the given questions using OpenAI."""
    responses = []
    base_prompt = utils.prompt()

    for q in questions:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": q}
            ],
            max_tokens=5,
            temperature=0
        )
        
        answer = response.choices[0].message['content'].strip()
        responses.append(answer if answer.isdigit() else "0")
    
    return responses

def link_job_apply(driver):
    generate_urls()
    count_applied = 0
    count_jobs = 0
    url_data = utils.getUrlDataFile()

    for url in url_data:
        driver.get(url)
        time.sleep(random.uniform(1, constants.botSpeed))

        try:
            total_jobs_element = retry_find_element(driver, By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal")
            total_jobs = total_jobs_element.text
            print(f"Total jobs found: {total_jobs}")
        except Exception as e:
            print(f"No matching jobs found or error in finding total jobs: {e}")
            continue

        total_pages = utils.jobsToPages(total_jobs)
        url_words = utils.urlToKeywords(url)
        display_write_results(f"\n Category: {url_words[0]}, Location: {url_words[1]}, Applying {total_jobs} jobs.")

        for page in range(total_pages):
            current_page_jobs = constants.jobsPerPage * page
            driver.get(url + "&start=" + str(current_page_jobs))
            time.sleep(random.uniform(1, constants.botSpeed))

            try:
                offers_per_page = retry_find_elements(driver, By.XPATH, '//li[@data-occludable-job-id]')
                offer_ids = [int(offer.get_attribute("data-occludable-job-id").split(":")[-1]) for offer in offers_per_page]
            except Exception as e:
                print(f"Error retrieving job offers on page {page}: {e}")
                continue

            for job_id in offer_ids:
                offer_page = f'https://www.linkedin.com/jobs/view/{job_id}'
                try:
                    driver.get(offer_page)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    count_jobs += 1
                    job_properties = get_job_properties(driver, count_jobs)
                    
                    button = easy_apply_button(driver)
                    if button:
                        button.click()
                        time.sleep(random.uniform(1, constants.botSpeed))
                        apply_for_job(driver, offer_page, job_properties)
                        count_applied += 1
                    else:
                        display_write_results(f"{job_properties} | * 🥳 Already applied! Job: {offer_page}")

                except Exception as e:
                    print(f"Error navigating to job page or applying: {e}")
                    save_screenshot_with_path(driver, f"error_job_{job_id}.png")
                    continue

        utils.prYellow(f"Category: {url_words[0]}, {url_words[1]} applied: {count_applied} jobs out of {count_jobs}.")



if __name__ == "__main__":
    driver = setup_driver()
    try:
        link_job_apply(driver)
    except Exception as e:
        utils.prRed(f"Error in main: {e}")
    finally:
        driver.quit()
