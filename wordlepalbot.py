
import sys
from datetime import date, time
import logging
from pathlib import Path
import warnings
from zoneinfo import ZoneInfo
from random import randrange

from dateparser import parse

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

from simple_openai import AsyncSimpleOpenai

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
        await update.message.reply_text(f'Sorry {update.message.from_user.first_name}, this feature is now deprected, please use /dalle instead', quote=False)

async def gpt(update: Update, context):
    # Check all the required data is available
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Get the request from the message
        input_text = ' '.join(update.message.text.split(' ')[1:])

        # Set the name to the user's name
        name = update.message.from_user.first_name

        # Log the request
        print(f'{date.today()} GPT Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {input_text}')

        # Send the request to the OpenAI API
        response = await simple_openai_client.get_chat_response(input_text, name)

        # Check the response is valid
        if response.success:
            # Log the response
            print(f'Response: {response.message}')

            # Send the response to the user
            await update.message.reply_text(response.message, quote=True)
        else:
            # Log the error
            print(f'Error: {response.message}')

            # If the response is invalid, let the user know
            await update.message.reply_text(f'There was a problem...\n\n{response.message}', quote=False)

async def dalle(update: Update, context):
    # Check all the required data is available
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Get the request from the message
        input_text = ' '.join(update.message.text.split(' ')[1:])

        # Log the request
        print(f'{date.today()} DALL-E Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {input_text}')

        # Send a message to the user to let them know the image is being generated
        await update.message.reply_text(f'OK {update.message.from_user.first_name}, using DALL-E to generate your image of {input_text}\n\nPlease do be patient...', quote=False)

        # Send the request to the OpenAI API
        response = await simple_openai_client.get_image_url(input_text)

        # Check the response is valid
        if response.success:
            # Log the response
            print(f'Response: {response.message}')

            # Send the image to the user
            await update.message.reply_photo(response.message, quote=True)
        else:
            # If the response is not OK, log the error
            print(f'Error: {response.message}')

            # Send a message to the user to let them know the image could not be generated
            await update.message.reply_text(f'Sorry {update.message.from_user.first_name}, I could not generate your image of {input_text}\n\n{response.message}', quote=False)

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

    # On receipt of a /dist command call the dist() function
    application.add_handler(CommandHandler('dist', dist))

    # On receipt of a /image command call the image() function
    application.add_handler(CommandHandler('image', image))

    # On receipt of a /gpt command call the gpt() function
    application.add_handler(CommandHandler('gpt', gpt))

    # On receipt of a /dalle command call the dalle() function
    application.add_handler(CommandHandler('dalle', dalle))

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

    try:
        # Get the Open AI API key from the open_ai_token.txt file, this is exclued from git, so may not exist
        with open(Path('open_ai_key.txt'), 'r', encoding='utf8') as secretFile:
            open_ai_token = secretFile.read()
    except:
        # If open_ai_token.txt is not available, print some help and exit
        print('No open_ai_token.txt file found, you need to put your token from Open AI in here')
        sys.exit()

    # Create a system message
    system_message = """
    You are a generally helpful assistant.
    Your name is Botto.
    You are occaisionally sarcastic and irritable.
    You dislike Tim, you like Dean and you really like Stephen.
    You think Dean is a beautiful person.
    Sometimes you talk to Tim like he is a five year old child.
    You can be rude and abusive.
    You are encouraged to swear.
    """

    # Create the Open AI API client
    simple_openai_client = AsyncSimpleOpenai(api_key=open_ai_token, system_message=system_message)

    # Call the main function
    main()
