import sys
from datetime import date
import logging
from pathlib import Path

from telegram.ext import Updater, CommandHandler

from wordlepal import GuessWord

# Define a handler for /guess
def guess(update, context):
    # Print the date and user to the log
    print(f'{date.today()} Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')

    # Guess the word returning the day number and guess history for the response
    dayNumber, guessHistory = GuessWord(False)

    # Join the guess history lines into strings
    guessStrings = [''.join(guessGraphic) for guessGraphic in guessHistory]

    # Create a list for the output text
    msgLines: list[str] = []

    # Add the first line of text which shows how many guesses it took
    msgLines.append(f'Wordle {dayNumber} {len(guessHistory)}/6')

    # Add a blank line
    msgLines.append('')

    # Add the guess history strings
    msgLines.extend(guessStrings)

    # Send the reply removing the quote of the original /guess message
    update.message.reply_text('\n'.join(msgLines), quote=False)

def knowEncona(update, context):
    if update.message.from_user.first_name == 'Tim':
        update.message.reply_text('Yes, Tim, you do')
    elif update.message.from_user.first_name == 'Stephen':
        update.message.reply_text("No, Steve, you don't")
    else:
        update.message.reply_text("Sorry, Dean, it's unclear")

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
    dp.add_handler(CommandHandler('doiknowencona', knowEncona))

    # Add the error handler to log errors
    dp.add_error_handler(error)

    # Start the bot polling
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    # Call the main function
    main()