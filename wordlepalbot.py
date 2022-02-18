import sys
from datetime import date
import logging
from pathlib import Path
import warnings

from dateparser import parse

from telegram.ext import Updater, CommandHandler

from WordList.WordList import Words

# Define a handler for /guess
def guess(update, context):
    # Print the date and user to the log
    print(f'{date.today()} Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')

    # Get the requested date
    commands: list[str] = update.message.text.split(' ')

    # Get the requested date if it exists in the command (only accessible by me)
    if len(commands) > 1:
        wordDate = parse(' '.join(commands[1:]), settings={'DATE_ORDER': 'DMY'})

        if wordDate is None:
            # If the date couldn't be parsed, let the user know and return
            update.message.reply_text(' '.join(commands[1:]))
            return
        else:
            # If the date was parsed, set it as the word date
            wordDate = wordDate.date()

        if update.message.from_user.first_name != 'Stephen' or update.message.from_user.last_name != 'Schleising':
            if wordDate > date.today():
                print(f'Future date requested: {wordDate}')
                update.message.reply_text(f"Sorry {update.message.from_user.first_name}, no peeking into the future for you")
                return
    else:
        # If no date is given use today's date
        wordDate = date.today()

    # Guess the word returning the day number and guess history for the response
    words = Words()
    words.GuessWord(wordDate=wordDate)

    # If the date is in bounds
    if not words.dateOutOfBounds:
        # Join the guess history lines into strings
        guessStrings = [''.join(guessGraphic) for guessGraphic in words.guessHistory]

        # Create a list for the output text
        msgLines: list[str] = []

        # Add the first line of text which shows how many guesses it took
        msgLines.append(f'Wordle {words.dayNumber} {words.guessNumberString}/6')

        # Add a blank line
        msgLines.append('')

        # Add the guess history strings
        msgLines.extend(guessStrings)

        # Send the reply removing the quote of the original /guess message
        update.message.reply_text('\n'.join(msgLines), quote=False)
    else:
        # State that the words have all been used up
        update.message.reply_text("It's all over, all the words have gone...")

# Log errors
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function
def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    try:
        # Get the token from the secret.txt file, this is exclued from git, so may not exist
        with open(Path('secret.txt'), 'r', encoding='utf8') as secretFile:
            token = secretFile.read()
    except:
        # If secret.txt is not available, print some help and exit
        print('No secret.txt file found, you need to put your token from BotFather in here')
        sys.exit()

    # Create the updater
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # On receipt of a /guess command call the guess() function
    dp.add_handler(CommandHandler('guess', guess))

    # Add the error handler to log errors
    dp.add_error_handler(error)

    # Start the bot polling
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    # Filter out a warning from dateparser
    warnings.filterwarnings('ignore', message='The localize method is no longer necessary')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    # Call the main function
    main()
