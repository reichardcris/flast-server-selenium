import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement as element
# from selenium.webdriver.firefox.webelement import FirefoxWebElement as element
from dotenv import load_dotenv
import json
import platform

class SeleniumAutomate:

  def __init__(self, pdf_path = '', pages = [], docs = {}):
    print("initiating credentials...")
    load_dotenv()

    # user creds

    self.user_name = os.getenv("HELLOSIGN_USERNAME")
    self.password = os.getenv("HELLOSIGN_PASSWORD")
    if (not self.user_name and not self.password):
      self.setStatus(401)
      return

    # pdf directory setup
    self.pdf_path = pdf_path
    self.pages = pages
    self.docs = docs
    dir = os.path.dirname(__file__)

    if (platform.system() == 'Darwin'):
      chrome_driver_path = dir + "/geckodriver"
    else:
      chrome_driver_path = dir + "\geckodriver.exe"

    driver = webdriver.Firefox(options = self.chromeOptions(), executable_path = chrome_driver_path)
    driver.maximize_window()
    driver.implicitly_wait(30)
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
    driver.get('https://app.hellosign.com/account/logIn')
    print("Starting The Browser...")


    self.login(driver)
    self.uploadFile(driver)
    self.addRecipient(driver)

    # Waiting for the Iframe editor
    self.waitElement(driver, '//*[@id="root"]/div/div[2]/div[1]/iframe', 5)
    driver.switch_to.frame(0)

    # PDF Editor Page
    time.sleep(2)
    self.waitElement(driver, '//*[@id="page-0"]/div/div[1]/img', 5)
    print('Switch to iFrame Editor')

    # When has a modal pop-up
    hasModal = self.waitElement(driver, '//*[@id="page-0"]/div/div[1]/img', 5)
    if (type(hasModal) is element):
      self.findElementByXPath(driver, '/html/body/div[6]/div/div/div/div[3]/div/button[1]').click()

    self.adjustZoomLevel(driver)
    self.finalStep(driver)
    self.setStatus()

  
  def setStatus(self, stat = 200):
    self.STATUS = stat
  
  def getStatus(self):
    return 'ok' if self.STATUS == 200 else 'Invalid Username Or Password', self.STATUS

  def findElementByXPath(self, driver, element = ''):
    element = driver.find_element_by_xpath(element)
    return element

  def waitElement(self, driver, path, attempts = 2, wait_time = 10):
    try:
        return WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, path))
        )
    except Exception as inst:
        if attempts:
            time.sleep(2)
            n = attempts-1
            self.waitElement(driver, path, n)
        return False

  def waitModalElement(self, driver, path, attempts = 2, wait_time = 10):
    try:
        return WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, path))
        )
    except Exception as inst:
        if attempts:
            time.sleep(2)
            n = attempts-1
            self.waitElement(driver, path, n)
        return False

  def chromeOptions(self):
    options = Options()
    options.add_argument('--webdriver-active')
    options.add_argument('--headless')
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-blink-features")
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    return options

  # Login System
  def login(self, driver):
    email_addresss = self.findElementByXPath(driver, '//input[@type="email"]')
    email_addresss.clear()
    email_addresss.send_keys(self.user_name)
    time.sleep(1)
    continue_button = self.findElementByXPath(driver, '/html/body/div[3]/div/div[3]/div[2]/div[1]/form/div[3]/div[2]/button')
    continue_button.click()
    time.sleep(1)
    password_ = self.findElementByXPath(driver, '//input[@type="password"]')
    password_.clear()
    password_.send_keys(self.password)
    time.sleep(1)
    login_button = self.findElementByXPath(driver, '/html/body/div[3]/div/div[3]/div[2]/div[1]/form/div[4]/div[2]/button')
    login_button.click()
    print("Login!...")

  # Procedure uploading
  def uploadFile(self, driver):
    print("initiating upload document...")
    time.sleep(3)
    sign_doc_btn = self.findElementByXPath(driver, '//div[text()="Sign Or Send"]')
    sign_doc_btn.click()

    # hasModalQuota = self.waitElement(driver, '/html/body/div[10]/div/div/div[@class="hello-modal"]', attempts = 0, wait_time = 0)
    # print('hasModalQuotahasModalQuotahasModalQuotahasModalQuota')
    # print(hasModalQuota)
    # if (type(hasModalQuota) is element):
    #   self.findElementByXPath(driver, '/html/body/div[10]/div/div/div/div[3]/div/button').click()

    file_dir = self.pdf_path
    file_input = self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[1]/span/input')
    file_input.send_keys(file_dir)

    time.sleep(1)
    next_button = self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div[2]/nav/div[2]/button[2]')
    next_button.click()

  # Recipient Stage
  def addRecipient(self, driver):
    print("initiating Recipient Details...")
    for index, val in enumerate(json.loads(self.docs['recepient'])):
      if (index > 0):
        time.sleep(1)
        self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div[1]/form/div[3]/div[1]/button').click()
      self.findElementByXPath(driver, f'//*[@id="recipients.{index}.name"]').send_keys(val['name'])
      self.findElementByXPath(driver, f'//*[@id="recipients.{index}.email"]').send_keys(val['email'])

    next_button = self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div[2]/nav/div[2]/button[2]')
    next_button.click()

  # Adjust the zoom level
  def adjustZoomLevel(self, driver):
    self.findElementByXPath(driver, '//*[@id="root"]/div/div/div[4]/div[2]/div').click()
    time.sleep(1)
    zoom_select = self.findElementByXPath(driver, '//*[@id="root"]/div/div/div[4]/div[2]/div/ul/li[2]')
    zoom_select.click()
  
  def removeAction(self, action):
    for device in action.w3c_actions.devices:
      device.clear_actions()
    
    return action


  def finalStep(self, driver):
    print("initiating signature boxes and dates...")
    page_counter = None
    xOffset = None
    yOffset = None
    img_page = None
    signature_file_counter = 0

    # time.sleep(1)

    for page_coordinates in self.pages:
      self.findElementByXPath(driver, '/html/body/div[1]/div/div/div[2]/div[2]').click()
      time.sleep(1)
      signer_selection = self.findElementByXPath(driver, f"/html/body/div[1]/div/div/div[2]/div[2]/ul/li/span[contains(text(), '{page_coordinates['type']}')]")
      signer_selection.click()
      # time.sleep(1)
      if page_counter != page_coordinates['page']:
        page_no = page_coordinates['page']
        pager = self.findElementByXPath(driver, f'//*[@id="root"]/div/div/div[3]/div[2]/div/div/div/div/div[@id="page-{page_no}"]/div/div/img')
        pager.click()
        # time.sleep(2)
        img_page = self.findElementByXPath(driver, f'//*[@id="page-{page_no}"]/div/div/img')
        

      xOffset = page_coordinates['x']
      yOffset = page_coordinates['y']
      action = ActionChains(driver)

      if (page_coordinates['field_type'] == 'date'):
        self.findElementByXPath(driver, '/html/body/div[1]/div/div/div[2]/div[7]/button').click()
        # time.sleep(1)
        action.move_to_element_with_offset(img_page, xOffset, yOffset).click().perform()
        action = self.removeAction(action)
        action.click(img_page)
        action = self.removeAction(action)

      else:
        # begin signature box placement
        self.findElementByXPath(driver, '/html/body/div[1]/div/div/div[2]/div[4]/button').click()
        action.move_to_element_with_offset(img_page, xOffset, yOffset).click().perform()
        signature_file_counter = signature_file_counter + 1

        # time.sleep(2)
        print('setting bullet adjustment->->->->->->')
        signature_bullet = self.findElementByXPath(driver, f'//*[@id="page-{page_no}"]/div/div[@data-field="Signature{signature_file_counter}"]/div/div/div/div[4]')
        signature_bullet_inner = self.findElementByXPath(driver, f'//*[@id="page-{page_no}"]/div/div[@data-field="Signature{signature_file_counter}"]/div/div/div/div[4]/div')
        action = self.removeAction(action)
        action.move_to_element(signature_bullet)
        action.click_and_hold()
        action.move_to_element_with_offset(signature_bullet, page_coordinates['w'], page_coordinates['h'])

        try:
          print('click_sigmatire bullet initiate!')
          action.click(signature_bullet_inner)
          action.perform()
        except Exception as inst:
          print('Error while clicking!!')
          action = self.removeAction(action)
          action.release()
          action.perform()


      action.reset_actions()
      action.move_to_element_with_offset(img_page, 5, 5).click().perform()
      self.removeAction(action)
      
      page_counter = page_coordinates['page']
      
    driver.switch_to.parent_frame()
    next_btn = self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div/nav/div[2]/button[2]')
    next_btn.click()


    document_title = self.findElementByXPath(driver, '//*[@id="document.title"]')
    document_title.send_keys(self.docs['document_title'])

    send_signature_btn = self.findElementByXPath(driver, '//*[@id="root"]/div/div[2]/div[1]/div[2]/nav/div[2]/button[2]')
    send_signature_btn.click()
    driver.quit()
    print("Done!")
