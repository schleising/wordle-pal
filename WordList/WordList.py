from datetime import date

from WordList.SolutionWords import SOLUTION_WORDS
from WordList.ValidWords import VALID_WORDS

class Words:
    def GetTodaysWord(self):
        return self.solutionWordlist[(date.today() - self.startDate).days]

    def __init__(self) -> None:
        self.startDate = date(2021, 6, 19)

        self.solutionWordlist = SOLUTION_WORDS
        self.validWordList = VALID_WORDS
    