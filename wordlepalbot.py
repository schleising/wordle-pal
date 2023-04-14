
import sys
from datetime import date, time
import logging
from pathlib import Path
import warnings
from zoneinfo import ZoneInfo

from dateparser import parse

from aiohttp import ClientSession

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

from WordList.WordList import Words
from wordlepal import RunGame, GenerateDistGraphic

# Define a handler for /guess
async def guess(update: Update, context):
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Print the date and user to the log
        print(f'{date.today()} Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')

        # Get the requested date
        commands: list[str] = update.message.text.split(' ')

        # Get the requested date if it exists in the command (only accessible by me)
        if len(commands) > 1:
            wordDate = parse(' '.join(commands[1:]), settings={'DATE_ORDER': 'DMY'})

            if wordDate is None:
                # If the date couldn't be parsed, let the user know and return
                await update.message.reply_text(' '.join(commands[1:]))
                return
            else:
                # If the date was parsed, set it as the word date
                wordDate = wordDate.date()

            if update.message.from_user.first_name != 'Stephen' or update.message.from_user.last_name != 'Schleising':
                if wordDate > date.today():
                    print(f'Future date requested: {wordDate}')
                    await update.message.reply_text(f"Sorry {update.message.from_user.first_name}, no peeking into the future for you")
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
            await update.message.reply_text('\n'.join(msgLines), quote=False)
        else:
            # State that the words have all been used up
            await update.message.reply_text("It's all over, all the words have gone...")

async def RunGameHandler(context: CallbackContext) -> None:
    # Run the game once a day to update the stats
    RunGame(wordDate=date.today(), downloadWords=True, writeFiles=True, verbose=True)

async def dist(update: Update, context):
    # Generate the image and return it without a quote
    with open(GenerateDistGraphic(), 'rb') as imageFile:
        if update.message is not None:
            await update.message.reply_photo(imageFile, quote=False)

async def image(update: Update, context):
    # Check all the required data is available
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Get the request from the message
        request = ' '.join(update.message.text.split(' ')[1:])

        # Log the request
        print(f'{date.today()} Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {request}')

        # Send a message to the user to let them know the image is being generated
        await update.message.reply_text(f'OK {update.message.from_user.first_name}, generating your image of {request}, please do be patient...', quote=False)

        # Open a session to the deepai API
        async with ClientSession() as session:
            # Post the request to the API
            async with session.post(
                "https://api.deepai.org/api/text2img",
                data={
                    'text': request,
                },
                headers={'api-key': deepai_token}
            ) as response:
                # If the response is OK
                if response.status == 200:
                    # Log the response
                    print(f'Response OK: {response.status}')

                    # Get the response as JSON
                    response_json = await response.json()

                    # Send the image to the user
                    await update.message.reply_photo(response_json['output_url'], quote=False)
                else:
                    # If the response is not OK, log the error
                    print(f'Error: {response.status}')

                    # Send a message to the user to let them know the image could not be generated
                    await update.message.reply_text(f'Sorry {update.message.from_user.first_name}, I could not generate your image of {request}, please try again later...', quote=False)

# Log errors
async def error(update, context):
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

    # Create the application
    application = ApplicationBuilder().token(token).build()

    # On receipt of a /guess command call the guess() function
    application.add_handler(CommandHandler('guess', guess))

    # On receipt of a /dist command call the guess() function
    application.add_handler(CommandHandler('dist', dist))

    # On receipt of a /image command call the guess() function
    application.add_handler(CommandHandler('image', image))

    # Add the error handler to log errors
    application.add_error_handler(error)

    # Get the JobQueue
    jq = application.job_queue

    # Start a daily job to run the game to keep the stats up to date
    if jq is not None:
        jq.run_daily(RunGameHandler, time(0, 0, 5, tzinfo=ZoneInfo('Europe/London')))

    # Start the bot polling
    application.run_polling()

if __name__ == '__main__':
    # Filter out a warning from dateparser
    warnings.filterwarnings('ignore', message='The localize method is no longer necessary')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    try:
        # Get the Deep AI API key from the deep_ai_token.txt file, this is exclued from git, so may not exist
        with open(Path('deep_ai_token.txt'), 'r', encoding='utf8') as secretFile:
            deepai_token = secretFile.read()
    except:
        # If deep_ai_token.txt is not available, print some help and exit
        print('No deep_ai_token.txt file found, you need to put your token from Deep AI in here')
        sys.exit()

    # Call the main function
    main()
