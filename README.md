# Chegg-Automation-using-Selenium-Python

This project is used for skipping questions in Chegg Expert Portal.

## Functionality of Project

The program when run with modified user credentials in the code, 
the program launches a firefox tab using geckodriver and loads the chegg expert login page.
Using the credentials the program logs in the user automatically and starts answering questions.
User can modify the "KEYWORDS_FOR_QUESTIONS_YOU_ANSWER" list in "Chegger" class in the code.
For each question the provided images in the question are converted into text using Pytesseract.
Now the keywords modified are used to check if question has any of them.
If any keywords are present then question stays else question is skipped automatically.
Thus the user can wait for the question which he can answer meanwhile the questions are skipped automatically.

## Aim of Project

The main aim of the project is to ease the skipping process which is much mechanical and too much time consuming.

## Tools Used 

* Selenium
* Tesseract

