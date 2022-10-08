from datetime import date

# Set the characters for good and bad letters
INCORRECT_LETTER = '⬜'
LETTER_IN_WORD = '🟨'
LETTER_IN_POSITION = '🟩'

# Set up the max letters in a word and the maximum number of guesses
MAX_LETTERS = 5
MAX_GUESSES = 6

START_DATE = date(2021, 6, 19)
DAY_OFFSET = 12546

FULL_IMAGE_SIZE = (750, 500)
GUESS_DISTRIBUTION_SIZE = (475, 50)
BAR_SCORE_SIZE = (750, 70)
SCORE_SIZE = (50, 70)
BAR_SIZE = (700, 70)

BASE_URL = 'https://www.nytimes.com/games/wordle/'
INDEX_PAGE = 'index.html'