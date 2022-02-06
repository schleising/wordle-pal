from datetime import date

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

class Words:
    def __init__(self) -> None:
        # Get the starting date
        self.startDate = date(2021, 6, 19)

        # Initialise the word lists
        self.solutionWordlist = SOLUTION_WORDS
        self.validWordList = VALID_WORDS

    @property
    def todaysWord(self) -> str:
        # Get the index into the solution word list from today's date
        return self.solutionWordlist[(date.today() - self.startDate).days].upper()
