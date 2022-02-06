from datetime import date
from collections import Counter

from WordList.TypeDefs import Word, Letter, WordScores, LetterScores

class Words:
    def __init__(self, wordList: list[Word]) -> None:
        # Get the starting date
        self._startDate = date(2021, 6, 19)

        # Initialise the word lists
        self._wordList: list[Word] = wordList

        # Concatenate the word lists
        self._letters = Letter().join(self._wordList)

        print()
        print(f'Number of Solutions   : {self.wordCount}')
        print(f"Today's Word is       : {self.todaysWord}")
        print()

        # Create counters of each letter
        self._letterCounter = self._CompileCounts()

        # Using the letter counts to score, score each valid word
        self._wordScores = self._CreateWordScores()

    @property
    def todaysWord(self) -> Word:
        # Get the index into the solution word list from today's date
        return self._wordList[(date.today() - self._startDate).days].upper()

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
