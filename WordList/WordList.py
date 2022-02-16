from datetime import date
from collections import Counter

from WordList.TypeDefs import Word, Letter, WordScores, LetterScores

class Words:
    def __init__(self, wordList: list[Word], wordDate: date = date.today()) -> None:
        # Get the starting date
        self._startDate = date(2021, 6, 19)

        # Print the wordDate for interest
        print(f'Words:__init__():wordDate : {wordDate}')

        # Initialise the word lists
        self._wordList: list[Word] = wordList

        # Get the day number
        self.dayNumber = (wordDate - self._startDate).days

        # Print the day number for interest
        print(f'Words:__init__():dayNumber: {self.dayNumber}')

        # Get today's word
        self.todaysWord = self._wordList[self.dayNumber]

        # Filter out the words that have already gone
        self._wordList = self._wordList[self.dayNumber:]

        # Concatenate the word lists
        self._letters = Letter().join(self._wordList)

        # Create counters of each letter
        self._letterCounter = self._CompileCounts()

        # Using the letter counts to score, score each valid word
        self._wordScores = self._CreateWordScores()

    @property
    def wordCount(self) -> int:
        return len(self._wordList)

    def _CompileCounts(self) -> Counter[Letter]:
        return Counter(self._letters)

    @property
    def soutionLetterCounterByFrequency(self) -> LetterScores:
        return dict(sorted(self._letterCounter.items(), key=lambda x: x[1], reverse=True))

    @property
    def soutionLetterCounterByLetter(self) -> LetterScores:
        return dict(sorted(self._letterCounter.items(), key=lambda x: x[0]))

    def _CreateWordScores(self) -> WordScores:
        # Create an empty dict to contain the scores for each word
        wordScores: WordScores = {}
    
        # Loop through all the solution words
        for word in self._wordList:
            # Set the word score to 0 for this word
            wordScores[word] = 0

            # Loop through the letters in the word
            for letter in set(word):
                # Add the score for this letter to the score for this word
                wordScores[word] += self._letterCounter[letter]

        return wordScores

    @property
    def wordScoresByScore(self):
        return dict(sorted(self._wordScores.items(), key=lambda x: x[1], reverse=True))
