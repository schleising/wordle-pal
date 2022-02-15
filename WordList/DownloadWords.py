import requests
import json

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

class WordDownloader():
    def __init__(self, url: str = 'https://www.nytimes.com/games/wordle/main.bd4cb59c.js') -> None:
        # Set the delimiters used to extract the words from the JavaScript
        self.solutionWordsDelimiter = 'Ma='
        self.validWordsDelimiter = ',Oa='
        self.endValidWordsDelimiter = ',Ra='
        self.url = url

        # If the JavaScript did not download correctly, use the defaults
        self.solutionWords = SOLUTION_WORDS
        self.validWords = VALID_WORDS

        # Get and parse the JavaScript
        self._DownloadWords()
        
    def _DownloadWords(self) -> None:
        # Get the JavaScript file
        response = requests.get(self.url)

        # Check the response code, if OK, update the defaults with the downloaded words
        if response.status_code == requests.codes.OK:
            # If the download was OK, get the full text
            fullText = response.text

            try:
                # Extract the text using the delimiters and load the JSON string into a Python list
                self.solutionWords: list[str] = json.loads(fullText.split(self.solutionWordsDelimiter)[1].split(self.validWordsDelimiter)[0])
                self.validWords: list[str] = json.loads(fullText.split(self.validWordsDelimiter)[1].split(self.endValidWordsDelimiter)[0])
            except:
                # If there is any kind of parsing error, reset the words back to the original ones
                self.solutionWords = SOLUTION_WORDS
                self.validWords = VALID_WORDS

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
