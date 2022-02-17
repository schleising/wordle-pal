from datetime import date, timedelta
from collections import Counter
from typing import Optional

from WordList.DownloadWords import WordDownloader
from WordList.TypeDefs import Word, Letter, WordScores, LetterScores
import WordList.Constants as Constants

class Words:
    def __init__(self, downloadWords: bool = True) -> None:
        # Get the starting date
        self._startDate = Constants.START_DATE

        # Get the solution and valid words
        wd = WordDownloader(downloadWords=downloadWords)

        # Initialise the word lists
        self._fullWordList: list[Word] = wd.solutionWords

        # Assume that the date is in bounds
        self.dateOutOfBounds = False

        # Set the dayNumber to 0
        self.dayNumber = 0

        # Set today's word to None
        self.todaysWord: Optional[str] = None

        # Filter out the words that have already gone
        self._remainingWordList: list[str] = []

        # Concatenate the word lists
        self._letters: str = ''

        # Create counters of each letter
        self._letterCounter: Counter[Letter] = Counter()

        # Using the letter counts to score, score each valid word
        self.wordScores: WordScores = WordScores()

        # Set up a string for the guess number
        self.guessNumberString: str = '0'

        # Set up the guess number
        self.guessNumber = 0

        # Set up a 6 x 5 array for the guess history
        self.guessHistory: list[list[str]] = []

    @property
    def fullWordCount(self) -> int:
        return len(self._fullWordList)

    @property
    def remainingWordCount(self) -> int:
        return len(self._remainingWordList)

    def _CompileCounts(self) -> None:
        self._letterCounter = Counter(self._letters)

    @property
    def soutionLetterCounterByFrequency(self) -> LetterScores:
        return dict(sorted(self._letterCounter.items(), key=lambda x: x[1], reverse=True))

    @property
    def soutionLetterCounterByLetter(self) -> LetterScores:
        return dict(sorted(self._letterCounter.items(), key=lambda x: x[0]))

    def _CreateWordScores(self) -> None:
        # Clear down the word scores dictionary
        self.wordScores.clear()

        # Loop through all the solution words
        for word in self._remainingWordList:
            # Set the word score to 0 for this word
            self.wordScores[word] = 0

            # Loop through the letters in the word
            for letter in set(word):
                # Add the score for this letter to the score for this word
                self.wordScores[word] += self._letterCounter[letter]

        # Sort the word scores by score, highest to lowest
        self.wordScores = dict(sorted(self.wordScores.items(), key=lambda x: x[1], reverse=True))

    def GuessWord(self, wordDate: date = date.today(), verbose: bool = False):
        # Check the date is not before the start date
        if wordDate < self._startDate:
            # Set the wordDate to the start date
            wordDate = self._startDate

            # Flag the date as out of bounds
            self.dateOutOfBounds = True

        # Check that the end date is in bounds
        if (wordDate - self._startDate).days >= len(self._fullWordList):
            # Set the wordDate to the last possible day
            wordDate = self._startDate + timedelta(days=len(self._fullWordList) - 1)

            # Flag the date as out of bounds
            self.dateOutOfBounds = True

        # Print the wordDate for interest
        print(f'Words:GuessWord():wordDate : {wordDate}')

        # Get the day number
        self.dayNumber = (wordDate - self._startDate).days

        # Print the day number for interest
        print(f'Words:GuessWord():dayNumber: {self.dayNumber}')

        # Get today's word
        self.todaysWord = self._fullWordList[self.dayNumber]

        # Filter out the words that have already gone
        self._remainingWordList = self._fullWordList[self.dayNumber:]

        # Set the guess number to 0 and set up an empty guess
        guess = ''

        # Loop over a maximum of six guesses until a match is found
        while self.guessNumber < Constants.MAX_GUESSES and guess != self.todaysWord:
            # Concatenate the word lists
            self._letters = Letter().join(self._remainingWordList)

            # Create counters of each letter
            self._CompileCounts()

            # Using the letter counts to score, score each valid word
            self._CreateWordScores()

            # Increment the guess number for humans
            self.guessNumber += 1

            # Get the highest scoring remaining word as the guess
            guess = list(self.wordScores)[0]

            if verbose:
                # Print the top 10 remaining words
                print()
                print(f'Top ten remaining words of {len(self.wordScores)}')
                print()
                print('===============================')
                print()
                for count, (word, score) in enumerate(list(self.wordScores.items())[:10]): print(f'{count + 1:2}) {word} - Score: {score}')
                print()

            # Set up the variables for good and bad letters and letter position tracking
            goodLetterPositions: list[Letter] = ['_' for _ in range(Constants.MAX_LETTERS)]
            goodLetters = ''
            badLetterPositions: list[Letter] = ['_' for _ in range(Constants.MAX_LETTERS)]
            excludedLetters = ''

            # Create a list for the guess graphic, initialised to all wrong guesses
            guessGraphic: list[str] = [Constants.INCORRECT_LETTER for _ in range(Constants.MAX_LETTERS)]

            # Loop over the letters in the guess word
            for count, letter in enumerate(guess):
                # If the letter is in the correct position, log this and continue
                if letter == self.todaysWord[count]:
                    goodLetterPositions[count] = letter

                    # Set the guess history in this guess line to the In Position character
                    guessGraphic[count] = Constants.LETTER_IN_POSITION

                    # Add to the string of good letters
                    goodLetters += letter
                else:
                    # We know that this letter is not in the correct position
                    goodLetterPositions[count] = '_'

                    # If the letter is in the word, but not in the correct position
                    if letter in self.todaysWord:
                        # State that this letter cannot appear in this position
                        badLetterPositions[count] = letter

                        # Set the guess history in this guess line to the letter in word character
                        guessGraphic[count] = Constants.LETTER_IN_WORD

                        # Add to the string of good letters
                        goodLetters += letter
                    else:
                        # This letter is not in the word, add it to the string of excluded letters
                        excludedLetters += letter

            # Append the guess graphic to the guess history
            self.guessHistory.append(guessGraphic)

            if verbose:
                # Print some stats
                print(f'Guess {self.guessNumber}                      : {" ".join(letter for letter in guess)}')
                print(f'                               {"".join(guessGraphic)}')
                print(f'Letters in correct positions : {" ".join(goodLetterPositions)}')
                print(f'Letters in bad positions     : {" ".join(badLetterPositions)}')
                print(f'Letters not in word          : {" ".join(excludedLetters)}')

            # Loop over a copy of the words remaining in contention
            for word in self.wordScores:
                # If any excluded letters are in this word, remove it from  the list
                if set(word) & set(excludedLetters):
                    self._remainingWordList.remove(word)
                # If there are good letters and they are not a subset of the word set, remove this word from the list
                elif set(goodLetters) and not set(goodLetters) <= set(word):
                    self._remainingWordList.remove(word)
                else:
                    # Loop over the letters in this word and remove if it does not have letters in known good postions 
                    # or it has letters in known bad positions
                    for index, letter in enumerate(word):
                        if (letter != goodLetterPositions[index] and goodLetterPositions[index] != '_' or
                            letter == badLetterPositions[index] and badLetterPositions[index] != '_'):
                            self._remainingWordList.remove(word)
                            break

        # Check whether the word was actually guessed
        if guess != self.todaysWord:
            # If not return 'X'
            self.guessNumberString = 'X'
        else:
            # If so, return the guess number as a string
            self.guessNumberString = str(self.guessNumber)

        if verbose:
            # Output the number of guesses it took
            print()
            print(f'Got the word {guess.upper()} in {self.guessNumber} attempts')
            print()

        # Output a Wordle like graphic
        print()
        print(f'Wordle {self.dayNumber} {self.guessNumberString}/6')
        print()

        for guessGraphic in self.guessHistory:
            print(''.join(guessGraphic))
