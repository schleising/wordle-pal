from datetime import date
from collections import Counter

from WordList.TypeDefs import Letter

from WordList.WordList import Words
from WordList.DownloadWords import WordDownloader

def GuessWord(writeFiles = True, verbose = False, wordDate: date = date.today()) -> tuple[int, list[list[str]]]:
    # Get the solution and valid words
    wd = WordDownloader()

    # Construct a Words object
    words = Words(wd.solutionWords, wordDate=wordDate)

    # Set the characters for good and bad letters
    incorrectLetter = '⬜'
    letterInWord = '🟨'
    letterInPosition = '🟩'

    # Set up the max letters in a word and the maximum number of guesses
    maxLetters = 5
    maxGuesses = 6

    # Set up a 6 x 5 array for the guess history
    guessHistory = [[incorrectLetter for _ in range(maxLetters)] for _ in range(maxGuesses)]

    # Set the guess number to 0 and set up an empty guess
    guessNumber = 0
    guess = ''

    # Get the list of solution words ordered by score
    fullSolutionList = words.wordScoresByScore

    # Copy the solution list into the filtered solution list, 
    # used to ensure that the list doesn't change while looping through it
    filteredSolutionList = dict(fullSolutionList)
    
    # Loop over a maximum of six guesses until a match is found
    while guessNumber < maxGuesses and guess != words.todaysWord:
        # Increment the guess number for humans
        guessNumber += 1

        # Get the highest scoring remaining word as the guess
        guess = list(filteredSolutionList)[0]

        if verbose:
            # Print the top 10 remaining words
            print()
            print(f'Top ten remaining words of {len(filteredSolutionList)}')
            print()
            print('===============================')
            print()
            for count, (word, score) in enumerate(list(filteredSolutionList.items())[:10]): print(f'{count + 1:2}) {word} - Score: {score}')
            print()

        # Set up the variables for good and bad letters and letter position tracking
        goodLetterPositions: list[Letter] = ['_' for _ in range(5)]
        goodLetters = ''
        badLetterPositions: list[Letter] = ['_' for _ in range(5)]
        excludedLetters = ''

        # Loop over the letters in the guess word
        for count, letter in enumerate(guess):
            # If the letter is in the correct position, log this and continue
            if letter == words.todaysWord[count]:
                goodLetterPositions[count] = letter

                # Set the guess history in this guess line to the In Position character
                guessHistory[guessNumber - 1][count] = letterInPosition

                # Add to the string of good letters
                goodLetters += letter
            else:
                # We know that this letter is not in the correct position
                goodLetterPositions[count] = '_'

                # If the letter is in the word, but not in the correct position
                if letter in words.todaysWord:
                    # State that this letter cannot appear in this position
                    badLetterPositions[count] = letter

                    # Set the guess history in this guess line to the letter in word character
                    guessHistory[guessNumber - 1][count] = letterInWord

                    # Add to the string of good letters
                    goodLetters += letter
                else:
                    # This letter is not in the word, add it to the string of excluded letters
                    excludedLetters += letter

        if verbose:
            # Print some stats
            print(f'Guess {guessNumber}                      : {" ".join(letter for letter in guess)}')
            print(f'                               {"".join(guessHistory[guessNumber - 1])}')
            print(f'Letters in correct positions : {" ".join(goodLetterPositions)}')
            print(f'Letters in bad positions     : {" ".join(badLetterPositions)}')
            print(f'Letters not in word          : {" ".join(excludedLetters)}')

        # Loop over a copy of the words remaining in contention
        for word in dict(filteredSolutionList):
            # If any excluded letters are in this word, remove it from  the list
            if set(word) & set(excludedLetters):
                filteredSolutionList.pop(word, None)
            # If there are good letters and they are not a subset of the word set, remove this word from the list
            elif set(goodLetters) and not set(goodLetters) <= set(word):
                filteredSolutionList.pop(word, None)
            else:
                # Loop over the letters in this word and remove if it does not have letters in known good postions 
                # or it has letters in known bad positions
                for index, letter in enumerate(word):
                    if (letter != goodLetterPositions[index] and goodLetterPositions[index] != '_' or
                        letter == badLetterPositions[index] and badLetterPositions[index] != '_'):
                        filteredSolutionList.pop(word, None)
                        break

    if verbose:
        # Output the number of guesses it took
        print()
        print(f'Got the word {guess.upper()} in {guessNumber} attempts')
        print()

    # Output a Wordle like graphic
    for guessGraphic in guessHistory[:guessNumber]:
        print(''.join(guessGraphic))

    if writeFiles:
        # Write the number of guesses to the history file 
        with open('history.txt', 'a', encoding='utf-8') as outputFile:
            outputFile.write(f'{guessNumber}\n')

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
            readmeFile.write(f"## Got today's word in {guessNumber} attempts</br>\n")

            for guessGraphic in guessHistory[:guessNumber]:
                readmeFile.write(f'{"".join(guessGraphic)}\\\n')
    
            readmeFile.write('</br>\n')

            readmeFile.write(f'## Average Number of Guesses: {averageScore:.2f}</br>\n')

            readmeFile.write('## Guess Statistics</br>\n')

            for count in range(maxGuesses):
                readmeFile.write(f'    {count+1}: {scoreCounts.get(count+1, 0)}\n')

            readmeFile.write('</br>\n\n')
    
            readmeFile.write('## Top 10 Starting Words (taken from remaining words)\n')

            for count, (word, score) in enumerate(list(words.wordScoresByScore.items())[:10]): readmeFile.write(f'    {count + 1:2}) {word.upper()} - Score: {score}\n')

            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n\n')

            readmeFile.write('## Today\'s Word\n')
            readmeFile.write(f'{words.todaysWord.upper()} - Updated {date.today().day:02}-{date.today().month:02}-{date.today().year}\n')

    return words.dayNumber, guessHistory[:guessNumber]

if __name__ == '__main__':
    GuessWord(verbose=True)
