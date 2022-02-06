import termplotlib as tpl

from WordList.WordList import Words
from WordList.SolutionWords import SOLUTION_WORDS

words = Words(SOLUTION_WORDS)
solutionCountsByLetter = words.soutionLetterCounterByLetter

print('Letter Frequency')
print('================')
print('')
fig = tpl.figure()
fig.barh(list(solutionCountsByLetter.values()), list(solutionCountsByLetter.keys()))
fig.show()

print()
print('Top ten first guess words')
print('=========================')
print()
for word, score in list(words.wordScoresByScore.items())[:10]: print(f'Word: {word}, Score: {score}')
