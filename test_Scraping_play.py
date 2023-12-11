import os
import time
import sys
import platform
import requests
import socket
import subprocess
import ctypes
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from tabulate import tabulate
from bs4 import BeautifulSoup


class IPAddress:
    def __init__(self, website_url):
        self.driver = None
        self.website_url = website_url
        self.website_ip = None
        self.website_name = None
        self.ipv4_address = None
        self.ipv6_address = None
        self.gateway_address = None
        self.api_endpoint = None

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_website_ip(self):
        try:
            self.website_ip = socket.gethostbyname(self.website_url)
            self.website_name = socket.gethostbyaddr(self.website_ip)[0]
            return self.website_ip
        except Exception as e:
            print(f"Error getting website IP address: {e}")
            return None


    def perform_data_extraction(self, duration, file_path):
        try:
            self.initialize_driver()
            chrome_options = webdriver.ChromeOptions()
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"Extracting data from {self.website_url} for {duration} seconds...")
            self.driver.get(self.website_url)

            time.sleep(duration)

            body_element = self.driver.find_element(By.XPATH, "//body")
            extracted_data = body_element.text

            with open(file_path, 'w') as file:
                file.write(extracted_data)

            print(f"Data saved to {file_path}")

        except Exception as e:
            print(f"Error occurred during data extraction: {e}")

        finally:
            self.close_driver()


    def extract_website_ip(self):
        try:
            parsed_uri = urlparse(self.website_url)
            domain = parsed_uri.netloc
            ip_address = socket.gethostbyname(domain)
            print(f"Website IP address for {domain}: {ip_address}")
            return ip_address
        except Exception as e:
            print(f"Error getting website IP address: {e}")
            return None


    def check_website_address(self, url):
        try:
            # Add scheme if missing (http:// or https://)
            if not url.startswith('http://') and not url.startswith('https://'):
                url = f'http://{url}'

            response = requests.head(url)
            if response.status_code == 200:
                print(f"Website address '{url}' is correct and active.")
                return True
            else:
                print(f"Website address '{url}' is incorrect or not active.")
                return False
        except requests.RequestException as e:
            print(f"Error occurred while checking website address: {e}")
            return False


    def get_ipv4_ipv6(self):
        try:
            self.ipv4_address = socket.gethostbyname(socket.gethostname())
            self.ipv6_address = [addrinfo[4][0] for addrinfo in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6)]
        except Exception as e:
            print(f"Error getting IPv4 and IPv6 addresses: {e}")

    def get_gateway_address(self):
        try:
            if self.is_admin():
                result = subprocess.run('ipconfig', shell=True, capture_output=True)
                output = result.stdout.decode('utf-8')
                gateway_lines = [line for line in output.split('\n') if 'Default Gateway' in line]
                if gateway_lines:
                    gateway_address = gateway_lines[0].split(':')[-1].strip()
                    self.gateway_address = gateway_address
                    return gateway_address
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error getting gateway address: {e}")
            return None


    def check_firewall(self):
        try:
            if self.website_ip:
                response = requests.get(f"http://{self.website_ip}")
                if response.status_code == 200:
                    return True
                else:
                    return False
            else:
                return None
        except Exception as e:
            print(f"Error checking firewall: {e}")
            return None


    def find_api_endpoint(self):
        try:
            response = requests.get(self.website_url)
            if response.status_code == 200:
                website_content = response.text
                api_endpoint_candidates = [
                    "api.website.com",  # Example API endpoint pattern
                    "api/v1",           # Another example pattern
                    # Add more patterns that might indicate the API endpoint
                ]

                found_endpoints = []

                for candidate in api_endpoint_candidates:
                    if candidate in website_content:
                        self.api_endpoint = candidate
                        found_endpoints.append(candidate)

                if found_endpoints:
                    print("Potential API endpoints found:")
                    with open('api_endpoints.txt', 'w', encoding='utf-8') as file:
                        for endpoint in found_endpoints:
                            ip_address = socket.gethostbyname(endpoint)
                            print(f"Endpoint: {endpoint}, IP Address: {ip_address}")
                            file.write(f"Endpoint: {endpoint}, IP Address: {ip_address}\n")
                else:
                    print("No potential API endpoints found on the website.")
            else:
                print("Failed to retrieve website content.")
        except Exception as e:
            print(f"Error occurred while finding the API endpoint: {e}")


    def dns_resolution_check(self, hosts):
        try:
            dns_server = '8.8.8.8'  # Using Google's DNS server as an example
            ip_addresses = []

            for host in hosts:
                response = requests.get(f"http://{dns_server}", headers={"Host": host})
                ip = socket.gethostbyname(host)
                ip_addresses.append([host, ip])

            if ip_addresses:
                headers = ["Host", "IP Address"]
                print(tabulate(ip_addresses, headers=headers))
                with open("dns_resolution.txt", "w", encoding="utf-8") as file:
                    file.write(tabulate(ip_addresses, headers=headers, tablefmt="plain"))
                print("DNS resolution check successful.")
            else:
                print("No IP addresses found.")
        except Exception as e:
            print(f"Error occurred during DNS resolution check: {e}")


    def get_website_ip_from_ping(self, url):
        try:
            # Initiating a ping request to get the IP address resolved from DNS
            ping_response = subprocess.Popen(['ping', url], stdout=subprocess.PIPE, shell=True)
            output, _ = ping_response.communicate()
            lines = output.decode('utf-8').splitlines()
            for line in lines:
                if 'Pinging' in line:
                    # Extracting IP address from the output of ping command
                    ip_address = line.split()[-1].strip('()')
                    print(f"IP address resolved from DNS: {ip_address}")
                    return ip_address
            print("Failed to extract IP address from ping response.")
            return None
        except Exception as e:
            print(f"Error occurred during ping request: {e}")
            return None


    def get_head_section_details(self):
        try:
            head_details = []
            self.driver.find_elements
            while True:
                # Extract details from the head section
                head_element = self.driver.find_element(By.XPATH, "//head")
                head_details.append(self.extract_element_data(head_element))
                # Write head details to a file (append mode)
                with open('head_details.txt', 'a+') as file:
                    file.write(str(head_details[-1]) + '\n')

        except Exception as e:
            print(f"Error occurred while getting head section details: {e}")
            head_details = []  # Reset to empty list in case of an error
        finally:
            self.head_section_details = head_details


    def get_headers(self):
        try:
            self.driver.get(self.website_url)
            # Maximum number of attempts to get the XPath
            attempts = 3
            self.driver.find_elements
            for _ in tqdm(range(attempts), desc="Fetching XPath"):
                self.xpath = self.get_xpath()
                if self.xpath:
                    # Print obtained XPath for debugging
                    print(f"Obtained XPath: {self.xpath}")
                    body_element = self.driver.find_element(By.XPATH, self.xpath)
                    if body_element:
                        elements = self.driver.find_elements(By.XPATH, self.xpath)
                        headers = [element.tag_name for element in elements if element.tag_name]
                        if not headers:
                            raise ValueError("Empty headers, extraction failed")
                        break
                    else:
                        raise ValueError("Empty data, headers extraction failed")
                else:
                    print("Getting XPath failed. Retrying...")
                    self.driver.refresh()  # Refresh the page to try again
                    time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            print(f"Error occurred during headers extraction: {e}")
            headers = []
        finally:
            self.headers = headers
            # Close the driver and print message about the session's closure
            # Assuming you have a method to close the driver
            self.close_driver()
            print("Connection has been closed successfully. Session closed.")


    def extract_element_data(self, element):
        try:
            # Extract element tag, classes, and styles
            element_data = []
            element_data.append(element.tag_name)
            element_data.append(element.get_attribute("class"))
            element_data.append(element.get_attribute("style"))
            return element_data
        except Exception as e:
            print(f"Error occurred during element data extraction: {e}")
            return []

class WebDataExtractor:
    def __init__(self, website_url):
        start_time = time.time()
        self.website_url = website_url
        self.driver = None
        self.action_times = {}
        self.initialize_driver()  # Initialize driver upon object creation
        self.xpath = None  # Initialize xpath attribute
        self.collected_data = []  # Initialize collected_data attribute

    def initialize_driver(self):
        try:
            start_time = time.time()
            chrome_options = webdriver.ChromeOptions()
            self.driver = webdriver.Chrome(options=chrome_options)
            elapsed_time = round(time.time() - start_time, 2)
            self.action_times['initialize_driver'] = elapsed_time
            print(f"Driver initialized successfully in {elapsed_time} seconds.")
        except WebDriverException as e:
            print(f"Error initializing the driver: {e}")


    def close_driver(self):
        try:
            start_time = time.time()
            if self.driver:
                self.driver.quit()
                elapsed_time = round(time.time() - start_time, 2)
                self.action_times['close_driver'] = elapsed_time
                print(f"Driver closed successfully in {elapsed_time} seconds.")
        except Exception as e:
            print(f"Error closing the driver: {e}")

    def get_xpath(self):
        start_time = time.time()
        # This method attempts to fetch the XPath of the body element using JavaScript
        return self.driver.execute_script(
            'function getPathTo(element) { \
                if (element.tagName === "HTML") \
                    return "/HTML[1]"; \
                if (element === document.body) \
                    return "/HTML[1]/BODY[1]"; \
                let ix = 0; \
                let siblings = element.parentNode.childNodes; \
                for (let i = 0; i < siblings.length; i++) { \
                    let sibling = siblings[i]; \
                    if (sibling === element) \
                        return (getPathTo(element.parentNode) + \
                            "/" + element.tagName + "[" + (ix + 1) + "]"); \
                    if (sibling.nodeType === 1 && \
                        sibling.tagName === element.tagName) \
                            ix++; \
                } \
            } \
            return getPathTo(arguments[0]);',
            self.driver.find_element(By.XPATH, "//body//*")
        )
        return self.xpath

    def extract_text(self):
        try:
            start_time = time.time()
            response = requests.get(self.website_url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                extracted_text = soup.get_text()
                elapsed_time = round(time.time() - start_time, 2)
                self.action_times['extract_text'] = elapsed_time
                return extracted_text
            else:
                print("Failed to retrieve website content.")
        except Exception as e:
            print(f"Error occurred while extracting text: {e}")
        return None

    def save_links(self, file_path):
        try:
            start_time = time.time()
            if not hasattr(self, 'website_url') or not self.website_url:
                raise ValueError("Website URL is not defined or is empty.")

            response = requests.get(self.website_url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                link_tags = soup.find_all('a')
                links = [link.get('href') for link in link_tags if link.get('href')]

                with open(file_path, 'w') as file:
                    file.write("\n".join(links))

                print(f"All links saved to {file_path}")
            else:
                print("Failed to retrieve website content.")
        except Exception as e:
            print(f"Error occurred while extracting links: {e}")

    def download_images(self, folder_path):
        try:
            start_time = time.time()
            response = requests.get(self.website_url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                img_tags = soup.find_all('img')
                img_urls = [img['src'] for img in img_tags if img.get('src')]

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                count = 0
                for idx, img_url in enumerate(img_urls):
                    if count >= 10:  # Adjust this number to the desired maximum number of images to download
                        break

                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        img_name = f'image_{idx}.jpg'
                        img_path = os.path.join(folder_path, img_name)
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_response.content)
                        print(f"Image {idx + 1} saved: {img_path}")
                        count += 1
                    else:
                        print(f"Failed to download image {idx + 1}")

                if count < 10:  # If fewer than 10 images are found on the page, print the actual count
                    print(f"Downloaded only {count} images.")
            else:
                print("Failed to retrieve website content.")
        except Exception as e:
            print(f"Error occurred while extracting images: {e}")

    def extract_images(self, folder_path, num_images=10):
        try:
            start_time = time.time()
            if self.driver:
                self.driver.get(self.website_url)

                # Collect image elements
                image_elements = self.driver.find_elements(By.TAG_NAME, 'img')  # Use By.TAG_NAME here
                if image_elements:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    count = 0
                    for idx, img_element in enumerate(image_elements):
                        if count >= num_images:
                            break

                        img_url = img_element.get_attribute('src')
                        if img_url:
                            img_response = requests.get(img_url)
                            if img_response.status_code == 200:
                                img_name = f'image_{idx}.jpg'  # Modify the naming scheme as needed
                                img_path = os.path.join(folder_path, img_name)
                                with open(img_path, 'wb') as img_file:
                                    img_file.write(img_response.content)
                                print(f"Image {idx + 1} saved: {img_path}")
                                count += 1
                            else:
                                print(f"Failed to download image {idx + 1}")
                    if count < num_images:
                        print(f"Extracted only {count} images out of {num_images}.")
                else:
                    print("No image elements found on the website.")
            else:
                print("Driver initialization failed. Image extraction aborted.")
        except Exception as e:
            print(f"Error occurred while extracting images: {e}")
        finally:
            self.close_driver()

    def close_driver(self):
        try:
            start_time = time.time()
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error closing the driver: {e}")


    def extract_styles(self):
        try:
            start_time = time.time()
            if self.driver:
                self.driver.get(self.website_url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                js_styles = self.driver.execute_script('''
                    var elements = document.querySelectorAll('*');
                    var styles = [];
                    elements.forEach(function(element) {
                        var computedStyles = window.getComputedStyle(element);
                        var elementStyles = {
                            "element": element.tagName.toLowerCase(),
                            "styles": computedStyles.cssText
                        };
                        styles.push(elementStyles);
                    });
                    return styles;
                ''')

                js_styles_file_path = 'js_styles.txt'
                with open(js_styles_file_path, 'w') as file:
                    for style in js_styles:
                        file.write(str(style) + '\n')

                print(f"JavaScript styles associated with HTML elements saved to {js_styles_file_path}")
            else:
                print("Driver initialization failed. Styles extraction aborted.")
        except Exception as e:
            print(f"Error occurred while extracting styles: {e}")

    def write_to_file(self, data, file_path):
        try:
            start_time = time.time()
            headers = ["Tag Name", "Classes", "Styles", "Div", 'Selectors', "Containers", "Container", "ID", "Body", ".div", "div"]
            formatted_data = [headers] + data

            # Writing action times and data in a tabular format
            with open(file_path, 'a+') as file:
                # Writing action times
                file.write("Action Times:\n")
                for action, action_time in self.action_times.items():
                    file.write(f"{action}: {action_time} seconds\n")
                file.write("\n")

                # Writing data in a tabular format
                table = tabulate(formatted_data, tablefmt="plain")
                file.write(table)
                file.write("\n\n")
                self.collected_data.extend(formatted_data)

                elapsed_time = round(time.time() - start_time, 2)
                print(f"Data successfully saved to {file_path} in {elapsed_time} seconds.")
        except Exception as e:
            print(f"Error occurred while writing data to file: {e}")
            print(f"Data saving to {file_path} failed.")


    def get_user_input(self):
        try:
            start_time = time.time()
            website_url = input("Enter the website address: ")
            file_path = input("Enter the file path to save the data: ")
            duration = int(input("Enter the duration of the script (in seconds): "))
            xpath = input("Enter the XPath of the website: ")
            elapsed_time = round(time.time() - start_time, 2)
            print(f"User input captured in {elapsed_time} seconds.")
            return website_url, file_path, duration, xpath
        except Exception as e:
            print(f"Error occurred during user input: {e}")
            return None, None, None, duration

    def run_extraction(self, website_ip, duration, file_path):
        try:
            start_time = time.time()
            print(f"Extracting data from {website_ip} for {duration} seconds...")

            # Your extraction logic here
            # Placeholder code; replace with your actual extraction process
            extracted_data = self.perform_extraction(duration)  # Perform the actual data extraction

            # Save the extracted data to the specified file path
            with open(file_path, 'w') as file:
                file.write(extracted_data)

            elapsed_time = round(time.time() - start_time, 2)
            print(f"Data extraction completed in {elapsed_time} seconds. Saved to {file_path}")
        except Exception as e:
            print(f"Error occurred during data extraction: {e}")


    def get_body_section_details(self):
        try:
            start_time = time.time()
            extraction_attempts = 0

            while extraction_attempts < 3:  # Perform extraction for a limited number of attempts
                # Extract details from the body section
                body_element = self.driver.find_element(By.XPATH, "//body")
                body_details = self.extract_element_data(body_element)

                # Write body details to a file (append mode)
                with open('body_details.txt', 'a') as file:
                    file.write(str(body_details) + '\n')

                extraction_attempts += 1

            elapsed_time = round(time.time() - start_time, 2)
            print(f"Body section details extracted in {elapsed_time} seconds and saved to body_details.txt")
        except Exception as e:
            print(f"Error occurred while getting body section details: {e}")
            raise ValueError("Failed to extract body section details")

    def perform_extraction(self, driver):
        try:
            start_time = time.time()

            text_elements = driver.find_elements(By.XPATH, "//your_text_element_xpath")
            text_data = [self.extract_text(elem) for elem in text_elements]

            link_elements = driver.find_elements(By.XPATH, "//your_link_element_xpath")
            link_data = [self.extract_links(elem) for elem in link_elements]

            image_elements = driver.find_elements(By.XPATH, "//your_image_element_xpath")
            image_data = [self.extract_images(elem) for elem in image_elements]

            data_mapping = {
                'text': text_data,
                'links': link_data,
                'images': image_data
            }

            elapsed_time = round(time.time() - start_time, 2)
            print(f"Extraction completed in {elapsed_time} seconds")
            return data_mapping
        except Exception as e:
            print(f"Error occurred during data extraction: {e}")
            return None


    def perform_data_extraction(self, duration, file_path):
        try:
            start_time = time.time()

            self.initialize_driver()
            print(f"Extracting data from {self.website_url} for {duration} seconds...")
            if self.driver:
                self.driver.get(self.website_url)
                time.sleep(duration)
                body_content = self.driver.find_element(By.XPATH, "//body").text

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(body_content)

                elapsed_time = round(time.time() - start_time, 2)
                print(f"Data extraction completed in {elapsed_time} seconds. Data saved to {file_path}")
            else:
                print("Driver initialization failed. Data extraction aborted.")
        except Exception as e:
            print(f"Error occurred during data extraction: {e}")
        finally:
            self.close_driver()


    def extract_media_queries(self, website_url, file_path):
        try:
            start_time = time.time()
            # Fetch the website content
            response = requests.get(website_url)
            if response.status_code == 200:
                html_content = response.text

                # Parse HTML content using BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all style tags containing media queries
                style_tags = soup.find_all('style')
                media_queries_content = []

                for style_tag in style_tags:
                    style_text = style_tag.get_text()
                    if '@media' in style_text:
                        media_queries_content.append(style_text)

                if media_queries_content:
                    # Save media queries to a file
                    with open(file_path, 'w') as file:
                        file.write("\n\n".join(media_queries_content))

                    elapsed_time = round(time.time() - start_time, 2)
                    print(f"Media queries structure saved to {file_path} in {elapsed_time} seconds")
                else:
                    print("No media queries found on the website.")
            else:
                print("Failed to retrieve website content.")
        except Exception as e:
            print(f"Error occurred while extracting media queries: {e}")

    def extract_body_data(self):
        try:
            start_time = time.time()
            elapsed_time = 0

            headers = self.get_headers()
            if headers:
                headers.insert(0, "Tag Name")  # Adding "Tag Name" as the first header
                self.write_to_file([headers], 'data.txt')  # Writing headers to file

                while elapsed_time < 60:
                    self.driver.refresh()
                    self.xpath = self.get_xpath()
                    body_element = self.driver.find_element(By.XPATH, self.xpath)
                    if body_element:
                        print("Data extracted from the body section successfully")
                        elements = self.driver.find_elements(By.XPATH, self.xpath)
                        element_details = [self.extract_element_data(element) for element in elements]
                        self.write_to_file(element_details, 'data.txt')
                    else:
                        raise ValueError("Empty data, extraction failed")
                    time.sleep(2)  # Pause for 2 seconds
                    print("Data extraction successful.")
                    elapsed_time = round(time.time() - start_time, 2)

                if elapsed_time >= 60:
                    print("Extraction time limit reached.")
            else:
                raise ValueError("Empty headers, extraction failed")
        except Exception as e:
            print(f"Error occurred: {e}")


    def extract_data(self, duration, file_path):
        try:
            start_time = time.time()
            end_time = start_time + duration

            print(f"Extracting data from {self.website_ip} for {duration} seconds...")

            while time.time() < end_time:
                # Your data extraction logic goes here using self.driver
                # Example: Scraping data from the website using self.driver.get(...)
                self.driver.get(f"http://{self.website_ip}")
                body_element = self.driver.find_element(By.XPATH, "//body")
                extracted_data = body_element.text

                # Save the extracted data to the file
                with open(file_path, 'w') as file:
                    file.write(extracted_data)

                print(f"Data saved to {file_path}")
                time.sleep(2)  # Wait for 2 seconds before re-extracting (adjust as needed)

            print("Extraction completed.")
        except Exception as e:
            print(f"Error occurred during data extraction: {e}")
        finally:
            # Close the driver after extraction
            self.close_driver()


if __name__ == "__main__":
    # Initialize the WebDataExtractor with a default URL or other data
    default_url = "https://pixabay.com/ro/music/"  # Replace this with your default URL or data
    web_extractor = WebDataExtractor(default_url)

    # Get the URL of the website from user input
    url = input("Enter the URL of the website: ")
    web_extractor.website_url = url  # Update the website URL

    try:
        web_extractor.initialize_driver()

        # Extract text content
        extracted_text = web_extractor.extract_text()
        if extracted_text:
            with open('extracted_text.txt', 'w', encoding='utf-8') as file:
                file.write(extracted_text)
            print("Text content extracted and saved to 'extracted_text.txt'")
        else:
            print("Failed to extract text content.")

        # Extract links
        web_extractor.save_links('links.txt')
        print("Links extracted and saved to 'links.txt'")

        # Extract images
        web_extractor.extract_images("P:\\Project Python\\Online Store\\venv\\Imagini extrase")
        print("Images extracted and saved to 'images' directory")

        web_extractor.download_images("P:\\Project Python\\Online Store\\venv\\Imagini extrase")
        web_extractor.get_body_section_details()
        web_extractor.perform_extraction()
        web_extractor.dns_resolution_check

        # Extract JavaScript files
        web_extractor.extract_javascript_files()
        print("JavaScript files extracted and saved to 'javascript_files' directory")

        # Extract body data
        body_data = web_extractor.extract_body_data()
        if body_data:
            with open('body_data.txt', 'w', encoding='utf-8') as file:
                file.write(body_data)
            print("Body data extracted and saved to 'body_data.txt'")
        else:
            print("Failed to extract body data.")

        # Perform data extraction
        data_extraction_result = web_extractor.perform_data_extraction()
        if data_extraction_result:
            print("Data extraction performed successfully.")
        else:
            print("Failed to perform data extraction.")

        # Perform extraction
        extraction_result = web_extractor.perform_extraction()
        if extraction_result:
            print("Extraction performed successfully.")
        else:
            print("Failed to perform extraction.")

    finally:
        web_extractor.close_driver()

