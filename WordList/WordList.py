from datetime import date
from collections import Counter

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

class Words:
    def __init__(self) -> None:
        # Get the starting date
        self._startDate = date(2021, 6, 19)

        # Initialise the word lists
        self._solutionWordlist = SOLUTION_WORDS
        self._validWordList = VALID_WORDS

        # Concatenate the word lists
        self._solutionLetters = ''.join(self._solutionWordlist)
        self._validLetters = ''.join(self._validWordList)

        print(f'Number of Solutions   : {self.solutionWordCount}')
        print(f'Number of Valid Words : {self.validnWordCount}')
        print()
        print(f"Today's Word is       : {self.todaysWord}")

        # Create counters of each letter
        self.soutionLetterCounter = self._CompileCounts(self._solutionLetters)
        self.validLetterCounter = self._CompileCounts(self._validLetters)

    @property
    def todaysWord(self) -> str:
        # Get the index into the solution word list from today's date
        return self._solutionWordlist[(date.today() - self._startDate).days].upper()

    @property
    def solutionWordCount(self) -> int:
        return len(self._solutionWordlist)

    @property
    def validnWordCount(self) -> int:
        return len(self._validWordList)

    def _CompileCounts(self, letters: str) -> Counter[str]:
        return Counter(letters)

    @property
    def soutionLetterCounterByFrequency(self) -> dict[str, int]:
        return dict(sorted(self.soutionLetterCounter.items(), key=lambda x: x[1], reverse=True))

    @property
    def validLetterCounterByFrequency(self) -> dict[str, int]:
        return dict(sorted(self.validLetterCounter.items(), key=lambda x: x[1], reverse=True))

    @property
    def soutionLetterCounterByLetter(self) -> dict[str, int]:
        return dict(sorted(self.soutionLetterCounter.items(), key=lambda x: x[0]))

    @property
    def validLetterCounterByLetter(self) -> dict[str, int]:
        return dict(sorted(self.validLetterCounter.items(), key=lambda x: x[0]))
