from datetime import date, timedelta
from collections import Counter
from pathlib import Path

from WordList.WordList import Words
import WordList.Constants as Constants

def RunGame(wordDate: date = date.today(), downloadWords: bool = False, writeFiles: bool = False, verbose: bool = False) -> Words:
    # Create a Words object using the 
    words = Words(downloadWords=downloadWords)

    # Guess the word
    words.GuessWord(wordDate=wordDate, verbose=verbose)

    if writeFiles:
        # Write the number of guesses to the history file 
        with open(Path('history.txt'), 'a', encoding='utf-8') as outputFile:
            outputFile.write(f'{words.guessNumber}\n')

        # Open the history file and get the new average score
        with open('history.txt', 'r', encoding='utf-8') as inputFile:
            # Create a list for the guess number history
            guessNumberHistory = [int(line) for line in inputFile]

        # Calculate the average score
        averageScore = sum(guessNumberHistory) / len(guessNumberHistory)

        # Output the average score
        print()
        print(f'Average Score: {averageScore:.2f}')

        # Get the counts of each score
        scoreCounts = Counter(guessNumberHistory)

        # Update the readme file
        with open('README.md', 'w') as readmeFile:
            readmeFile.write('[![Python application](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml/badge.svg)](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml)\n')
            readmeFile.write('# wordle-pal\n')
            readmeFile.write('## Help with Wordle words\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n\n')
            readmeFile.write(f"## Got today's word in {words.guessNumber} attempts</br>\n")

            for guessGraphic in words.guessHistory:
                readmeFile.write(f'{"".join(guessGraphic)}\\\n')
    
            readmeFile.write('</br>\n')

            readmeFile.write(f'## Average Number of Guesses: {averageScore:.2f}</br>\n')

            readmeFile.write('## Guess Statistics</br>\n')

            for count in range(Constants.MAX_GUESSES):
                readmeFile.write(f'    {count+1}: {scoreCounts.get(count+1, 0)}\n')

            readmeFile.write('</br>\n\n')
    
            readmeFile.write('## Top 10 Starting Words (taken from remaining words)\n')

            for count, (word, score) in enumerate(list(words.wordScores.items())[:10]): readmeFile.write(f'    {count + 1:2}) {word.upper()} - Score: {score}\n')

            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n\n')

            readmeFile.write('## Today\'s Word\n')
            readmeFile.write(f'{words.todaysWord.upper() if words.todaysWord is not None else ""} - Updated {date.today().day:02}-{date.today().month:02}-{date.today().year}\n')

    return words

def RunCompleteGame() -> None:
    currentDate = Constants.START_DATE

    with open(Path('Output.txt'), 'w', encoding='utf-8') as outputFile:
        while True:
            words = RunGame(wordDate=currentDate, writeFiles=True)

            if words.dateOutOfBounds:
                break

            print('===============')
            print(f'Wordle {words.dayNumber} {words.guessNumberString}/6')
            print()

            # Output a Wordle like graphic
            for guessGraphic in words.guessHistory:
                print(''.join(guessGraphic))

            outputFile.write('===============\n')
            outputFile.write(f'Wordle {words.dayNumber} {words.guessNumberString}/6\n')
            outputFile.write('\n')

            # Output a Wordle like graphic
            for guessGraphic in words.guessHistory:
                outputFile.write(f"{''.join(guessGraphic)}\n")

            currentDate = currentDate + timedelta(days=1)

if __name__ == '__main__':
    RunGame(downloadWords=True, writeFiles=True, verbose=True)

    # RunCompleteGame()
