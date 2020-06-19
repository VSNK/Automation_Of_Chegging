from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from PIL import Image
from time import sleep
import pytesseract
import logging
from urllib.parse import urlparse
import playsound
import time
import re

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #make sure your tesseract is installed in this path if not change the path


class Chegger():

	TOTAL_ANSWERED = 0 
	TOTAL_SKIPPED = 0
	CHEGG_LOGIN = "https://www.chegg.com/auth?action=login"
	CHEGG_EXPERT_QA = "https://www.chegg.com/my/expertqa"
	CHEGG_QA = "https://expert.chegg.com/expertqna"
	PAUSE_FOR = 500 #the program pauses for every 500 questions skipped and asks you whether to continue or not. you can change the value 
	

	KEYWORDS_FOR_QUESTIONS_YOU_ANSWER = \
	[	
		"py", "python",
		"js", "javascript",
		"java", "def", "class", "dbms", "db"
		"c lang", "c++", "cpp"
		"html", "css", "php", "jquery", "bootstrap"
		"choose", "option" , "choose the correct answer"
		"verify", "aws", 
		"linux", "shell" , "bash", "cmd"
						]

	def __init__(self, email, pswd):
		self.driver = webdriver.Firefox()
		self.wait = WebDriverWait(self.driver, 100)
		logging.info("Firefox Webdriver initialized...")
		self.email = email
		self.pswd = pswd
		self.skipped = 0
		self.answered = 0

	def reboot(self):
		self.driver.quit()
		driver = webdriver.Firefox()
		self.__init__(email, pswd)

	def quit(self):
		logging.info("Quitting program...")
		self.driver.quit()
		exit()

	def run(self):
		# try:
		count = 0
		prev = -1
		now = 0
		self.login()
		self.wait_for_url(Chegger.CHEGG_LOGIN)
		logging.info("Logged in successfully")
		logging.info("Redirecting to "+Chegger.CHEGG_EXPERT_QA+" ...")
		self.driver.get(Chegger.CHEGG_EXPERT_QA)
		self.wait_for_url(Chegger.CHEGG_EXPERT_QA)
		logging.info("Starting to answer")
		self.start_answering()
		while True:
			if self.is_current_url(Chegger.CHEGG_EXPERT_QA):
				self.start_answering()
			self.wait_for_url(Chegger.CHEGG_QA)
			now = self.get_element("(//div[@data-test-id='skipped']//span)[2]").text
			
			_question = self.question()
			_reply = self.categorizer(_question)
			if _reply:
				try:
					playsound.playsound("boss.mp3")
				except:
					pass
				_input = input("program paused(press enter to continue)")
				_status = input("Have you answered the question(y/n)? ")
				if _status.lower() in ("y","yeah","yes","yep"):
					pass
				else:
					self.skip()


			else:
				self.skip()
			if count==Chegger.PAUSE_FOR:
				_status = input("Would you like to continue(y/n)? ")
				if _status in ("y","yeah","yes","yep"):
					count = 0
					pass
				else:
					logging.info("Stopping the program...")
					break
			count += 1

		
	def login(self):
		logging.info("Logging into "+Chegger.CHEGG_LOGIN+ " ...")
		self.driver.get(Chegger.CHEGG_LOGIN)
		_username = self.get_element("//input[@id='emailForSignIn']")
		_password = self.get_element("//input[@id='passwordForSignIn']")
		_submit	 = self.get_element("//button[@name='login']")
		logging.info("\t* Filled email field with "+self.email)
		_username.send_keys(self.email)
		time.sleep(1)
		logging.info("\t* Filled password field with "+self.pswd)
		_password.send_keys(self.pswd)
		logging.info("\t* Submittiing form...")
		self.driver.execute_script("arguments[0].click();", _submit)
		logging.info("Logged in successfully")


	def start_answering(self):
		logging.info("Starting to answer questions...")
		_start_answering = self.get_element("//button[text()='Start answering questions']")
		self.driver.execute_script("arguments[0].click();", _start_answering)

	def skip(self):	
		self.wait_for_url(Chegger.CHEGG_QA)	
		self.skipped += 1
		_question = self.get_element("//div[@data-test-id='question']")

		logging.info("Skipping question no "+str(self.skipped))
		_skip = self.get_element("//span[text()='Skip']")
		try:
			self.driver.execute_script("arguments[0].click();", _skip)
		except:
			time.sleep(1)
			self.driver.execute_script("arguments[0].click();", _skip)
        
		_i_dont_have_knowledge = self.get_element("//label[contains(text(),'I don')]")
		self.driver.execute_script("arguments[0].click();", _i_dont_have_knowledge)

		_topic = self.get_element("//span[contains(text(),'What topic should it be?')]")
		self.driver.execute_script("arguments[0].click();", _topic)

		logging.info("Skipping as Other Computer Science ...")
		_category = self.get_element("//li[contains(text(),'Other Computer Science')]")
		self.driver.execute_script("arguments[0].click();", _category)

		logging.info("Submitting response...")
		_submit = self.get_element("//span[text()='Submit']")
		self.driver.execute_script("arguments[0].click();", _submit)
		logging.info("Skipped question successfully ...")

		while _question == self.get_element("//div[@data-test-id='question']"):
			time.sleep(0.5)

	def question(self):
		self.wait_for_url(Chegger.CHEGG_QA)
		logging.info("Started to fetch question ...")
		_question = self.get_element("//div[@data-test-id='question']")
		_paragraphs = _question.find_elements("xpath","//p")
		_text = ""
		_images = _question.find_elements("xpath","//img")
		_urls = list()
		logging.info("\t* Getting urls of images")
		for img in _images:
			_urls.append(img.get_attribute("src"))
		logging.info("\t* "+str(len(_urls))+" images are found in question")

		for para in _paragraphs:
			_text += para.text+" "

		logging.info("Converting images to text using tesseract ...")
		for url in _urls:
			name=url.split("/")[-1]
			if "." not in name:
				continue
			image = open("images\\"+name, "wb")
			try:
				image.write(requests.get(url, allow_redirects=True).content)
			except:
				continue
			try:
				_text += pytesseract.image_to_string(Image.open("images\\"+name)) + " "
			except:
				pass
			image.close()

		logging.info("Question extracted successfully from images and user added text ...")
		logging.info(f"Question\n{_text}")
		return _text

	def answer(self):
		self.wait_for_url(Chegger.CHEGG_QA)
		logging.info("Answering to question ...")
		_answer = self.get_element("//span[text()='Answer']")
		self.driver.execute_script("arguments[0].click();", _answer)

	@classmethod			#this method you can modify as your wish it basically searches for keywords in a given-question-as-text
	def categorizer(cls, question):	
		logging.info("Searching for key words in question ...")
		_flag = 0
		words = cls.KEYWORDS_FOR_QUESTIONS_YOU_ANSWER
		for i in set(question):
			if ord(i) not in [*range(65,91),*range(97,123),*range(48,58)]:
				question=question.replace(i," ")
		# _flag = len(re.findall("|".join(words),question.lower()))
		recognized = []
		for i in question.split():
			for j in words:
				if j in i:
					if j not in recognized:
						recognized.append(j)
						print("* "+j)
					_flag += 1

		if _flag==0:
			logging.info("No keywords found")
		return _flag

	def is_current_url(self, url):
		u1 = urlparse(url)
		u2 = urlparse(self.driver.current_url)
		_flag = True
		for i in range(3):
			if u1[i]!=u2[i]:
				_flag = False
		return _flag

	def get_element(self, path):
		element = ""
		try:
		    element = self.wait.until(
		        EC.presence_of_element_located(("xpath", path))
		    )
		finally:
		    return element

	def wait_for_url(self, url):
		logging.info("If the url is not loading please load it manually")
		logging.info("Until then program waits...")
		self.wait.until(EC.url_to_be(url))
	

if __name__=="__main__":
	chegger = Chegger("put your email", "replace this with your password")
	chegger.run()
