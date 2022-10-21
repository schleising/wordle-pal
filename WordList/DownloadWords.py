import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
import requests
import json
import re

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

from WordList.Constants import BASE_URL, DAY_OFFSET, INDEX_PAGE

class WordDownloader():
    def __init__(self, url: str = f'{BASE_URL}{INDEX_PAGE}', downloadWords: bool = True) -> None:
        # Set the delimiters used to extract the words from the JavaScript
        self._url = url

        # Use the defaults to start with
        self.solutionWords = SOLUTION_WORDS
        self.validWords = VALID_WORDS

        # Get and parse the JavaScript if requested to update the words
        if downloadWords:
            self._DownloadWords()
        
    def _DownloadWords(self) -> None:
        try:
            # Get the HTML file
            response = requests.get(self._url)

            # Check the response code, if OK, update the defaults with the downloaded words
            if response.status_code == requests.codes.OK:
                # If the download was OK, get the full text
                fullText = response.text

                # Compile a regex to match the javascript file
                jsRegex = re.compile(r'https://www\.nytimes\.com/games-assets/v2/wordle\.[a-f0-9]+\.js')

                # Find the current name of the javascript file
                jsFile = jsRegex.search(fullText)

                # If there is a match, download the js file
                if jsFile:
                    # Get the JavaScript file
                    response = requests.get(f'{jsFile.group()}')

                    if response.status_code == requests.codes.OK:
                        # Get the text
                        fullText = response.text
                        
                        # Compile a regex to match a JS list of five character strings
                        # surrounded by square brackets that may or may not have commas
                        wordRegex = re.compile(r'(\[("[a-z]{5}",?)+\])')

                        # Find the matches
                        wordLists = wordRegex.findall(fullText)

                        # The first match is the list of words
                        allWords = json.loads(wordLists[0][0])

                        # The valid words are in the first part of the list
                        self.validWords = allWords[:DAY_OFFSET]

                        # The solutions are in the second part of the list
                        self.solutionWords = allWords[DAY_OFFSET:]
                    else:
                        # If there is any kind of download or parsing error, reset the words back to the original ones
                        self.solutionWords = SOLUTION_WORDS
                        self.validWords = VALID_WORDS

                        # Indicate that we are using defaults
                        print('Download or parsing failed, using default word lists')

                        # Send an email to indicate failure
                        self._SendFailureEmail(1)
                else:
                    # If there is any kind of download or parsing error, reset the words back to the original ones
                    self.solutionWords = SOLUTION_WORDS
                    self.validWords = VALID_WORDS

                    # Indicate that we are using defaults
                    print('Download or parsing failed, using default word lists')

                    # Send an email to indicate failure
                    self._SendFailureEmail(2)
            else:
                # If there is any kind of download or parsing error, reset the words back to the original ones
                self.solutionWords = SOLUTION_WORDS
                self.validWords = VALID_WORDS

                # Indicate that we are using defaults
                print('Download or parsing failed, using default word lists')

                # Send an email to indicate failure
                self._SendFailureEmail(3)
        except:
            # If there is any kind of download or parsing error, reset the words back to the original ones
            self.solutionWords = SOLUTION_WORDS
            self.validWords = VALID_WORDS

            # Indicate that we are using defaults
            print('Download or parsing failed, using default word lists')

            # Send an email to indicate failure
            self._SendFailureEmail(4)
        else:
            # Show that the words were downloaded OK
            print('Downloaded words succesfully')

            # If download and parsing was successful, update the default solution and
            # valid word files in case of changes for use another day if necessary
            with open(Path('WordList/SolutionWords.py'), 'w', encoding='utf-8') as solutionFile:
                wordList = json.dumps(self.solutionWords)
                solutionFile.write(f'SOLUTION_WORDS: list[str] = {wordList}')

            with open(Path('WordList/ValidWords.py'), 'w', encoding='utf-8') as validFile:
                wordList = json.dumps(self.validWords)
                validFile.write(f'VALID_WORDS: list[str] = {wordList}')

    def _SendFailureEmail(self, errorCode: int) -> None:
        username = os.environ.get('GMAIL_ENV_USER', None)
        password = os.environ.get('GMAIL_ENV_PASS', None)

        if username and password:
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.ehlo()
                    server.login(username, password)

                    msg = EmailMessage()
                    msg.set_content(f'There was a problem downloading the word lists: {errorCode}')
                    msg['Subject'] = 'Wordlepal - There was a problem'
                    msg['From'] = 'Stephen Schleising <stephen@schleising.net>'
                    msg['To'] = 'Stephen Schleising <stephen@schleising.net>'

                    server.send_message(msg)

                    print(f'Email sent: There was a problem downloading the word lists: {errorCode}')
            except:
                print('Something went wrong')
        else:
            print('Cannot send email notification')

if __name__ == '__main__':
    # Test this class
    wd = WordDownloader()

    # Print the downloaded words
    print()
    print('Solutions Words')
    print('===============')
    print(wd.solutionWords)

    print()
    print('Valid Words')
    print('===========')
    print(wd.validWords)
