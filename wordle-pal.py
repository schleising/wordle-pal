import termplotlib as tpl

from WordList.WordList import Words

words = Words()
solutionCountsByLetter = words.soutionLetterCounterByLetter

fig = tpl.figure()

fig.barh(list(solutionCountsByLetter.values()), list(solutionCountsByLetter.keys()))
fig.show()
