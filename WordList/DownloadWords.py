import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
import requests
import json

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

class WordDownloader():
    def __init__(self, url: str = 'https://www.nytimes.com/games/wordle/main.3d28acc.js', downloadWords: bool = True) -> None:
        # Set the delimiters used to extract the words from the JavaScript
        self._solutionWordsDelimiter = 'Ma='
        self._validWordsDelimiter = ',Oa='
        self._endValidWordsDelimiter = ',Ra='
        self._url = url

        # Use the defaults to start with
        self.solutionWords = SOLUTION_WORDS
        self.validWords = VALID_WORDS

        # Get and parse the JavaScript if requested to update the words
        if downloadWords:
            self._DownloadWords()
        
    def _DownloadWords(self) -> None:
        try:
            # Get the JavaScript file
            response = requests.get(self._url)

            # Check the response code, if OK, update the defaults with the downloaded words
            if response.status_code == requests.codes.OK:
                # If the download was OK, get the full text
                fullText = response.text

                # Extract the text using the delimiters and load the JSON string into a Python list
                self.solutionWords: list[str] = json.loads(fullText.split(self._solutionWordsDelimiter)[1].split(self._validWordsDelimiter)[0])
                self.validWords: list[str] = json.loads(fullText.split(self._validWordsDelimiter)[1].split(self._endValidWordsDelimiter)[0])
            else:
                # If there is any kind of download or parsing error, reset the words back to the original ones
                self.solutionWords = SOLUTION_WORDS
                self.validWords = VALID_WORDS

                # Indicate that we are using defaults
                print('Download or parsing failed, using default word lists')

                # Send an email to indicate failure
                self._SendFailureEmail()
        except:
            # If there is any kind of download or parsing error, reset the words back to the original ones
            self.solutionWords = SOLUTION_WORDS
            self.validWords = VALID_WORDS

            # Indicate that we are using defaults
            print('Download or parsing failed, using default word lists')

            # Send an email to indicate failure
            self._SendFailureEmail()
        else:
            # If download and parsing was successful, update the default solution and
            # valid word files in case of changes for use another day if necessary
            with open(Path('WordList/SolutionWords.py'), 'w', encoding='utf-8') as solutionFile:
                wordList = json.dumps(self.solutionWords)
                solutionFile.write(f'SOLUTION_WORDS: list[str] = {wordList}')

            with open(Path('WordList/ValidWords.py'), 'w', encoding='utf-8') as validFile:
                wordList = json.dumps(self.validWords)
                validFile.write(f'VALID_WORDS: list[str] = {wordList}')

    def _SendFailureEmail(self) -> None:
        username = os.environ['GMAIL_ENV_USER']
        password = os.environ['GMAIL_ENV_PASS']

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.ehlo()
                server.login(username, password)

                msg = EmailMessage()
                msg.set_content('There was a problem downloading the word lists')
                msg['Subject'] = 'Wordlepal - There was a problem'
                msg['From'] = 'Stephen Schleising <stephen@schleising.net>'
                msg['To'] = 'Stephen Schleising <stephen@schleising.net>'

                server.send_message(msg)
        except:
            print('Something went wrong')

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
