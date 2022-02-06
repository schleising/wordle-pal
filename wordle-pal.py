from datetime import date

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

with open('README.md', 'w') as readmeFile:
    readmeFile.write('[![Python application](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml/badge.svg)](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml)\n')
    readmeFile.write('# wordle-pal\n')
    readmeFile.write('Help with Wordle words\n')
    readmeFile.write('<br>\n')
    readmeFile.write('<br>\n\n')
    readmeFile.write('## Top 10 Starting Words\n')

    for count, (word, score) in enumerate(list(words.wordScoresByScore.items())[:10]): readmeFile.write(f'    {count + 1:2}) {word.upper()} - Score: {score}\n')

    readmeFile.write('<br>\n')
    readmeFile.write('<br>\n\n')

    readmeFile.write('## Today\'s Word\n')
    readmeFile.write(f'{words.todaysWord} - Updated {date.today().day:02}-{date.today().month:02}-{date.today().year}\n')
