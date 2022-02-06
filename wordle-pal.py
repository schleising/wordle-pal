import termplotlib as tpl

from WordList.WordList import Words
from WordList.SolutionWords import SOLUTION_WORDS

words = Words(SOLUTION_WORDS)

print('Letter Frequency')
print('================')
print('')
solutionCountsByLetter = words.soutionLetterCounterByLetter
fig = tpl.figure()
fig.barh(list(solutionCountsByLetter.values()), list(solutionCountsByLetter.keys()))
fig.show()

print()
print('Top ten first guess words')
print('=========================')
print()
for count, (word, score) in enumerate(list(words.wordScoresByScore.items())[:10]): print(f'{count + 1:2}) {word.upper()} - Score: {score}')
