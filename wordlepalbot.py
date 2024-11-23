
import json
import sys
from datetime import date
import logging
from pathlib import Path
import warnings

import aiohttp

from dateparser import parse

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

from simple_openai import AsyncSimpleOpenai
from simple_openai.models import open_ai_models

from WordList.WordList import Words
from wordlepal import RunGame, GenerateDistGraphic

FOOTBALL_API_BASE_URL  = 'https://schleising.net'
FOOTBALL_API_MATCH_URL = '/football/api'

# Define the storage path
storage_path = Path('/storage')

# File containing the last dalle request per user
last_dalle_request_file = storage_path / 'last_dalle_request.json'

# Load the last dalle request per user
if last_dalle_request_file.exists():
    with open(last_dalle_request_file, 'r') as file:
        last_dalle_requests = json.load(file)
        print(f'Loaded last dalle requests: {last_dalle_requests}')
else:
    last_dalle_requests: dict[str, str] = {}
    print('No last dalle requests found')

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
        await update.message.reply_text(f'Sorry {update.message.from_user.first_name}, this feature is now deprecated, please use /dalle instead', quote=False)

async def gpt(update: Update, context):
    # Check all the required data is available
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Send a typing action to the user
        await update.get_bot().send_chat_action(update.message.chat.id, 'typing')

        # Get the request from the message
        input_text = ' '.join(update.message.text.split(' ')[1:])

        # Set the name to the user's name
        name = update.message.from_user.first_name

        # Log the request
        print(f'{date.today()} GPT Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {input_text}')

        # Send the request to the OpenAI API
        response = await simple_openai_client.get_chat_response(input_text, name, str(update.message.chat.id), add_date_time=True)

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
        # Send an upload photo action to the user
        await update.get_bot().send_chat_action(update.message.chat.id, 'upload_photo')

        # Get the request from the message
        input_text = ' '.join(update.message.text.split(' ')[1:])

        # Log the request
        print(f'{date.today()} DALL-E Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {input_text}')

        # Store the last dalle request per user
        last_dalle_requests[f'{update.message.from_user.id}-{update.message.chat_id}'] = input_text

        # Save the last dalle request per user
        with open(last_dalle_request_file, 'w') as file:
            json.dump(last_dalle_requests, file)

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

async def remix(update: Update, context):
    # Check all the required data is available
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Send an upload photo action to the user
        await update.get_bot().send_chat_action(update.message.chat.id, 'upload_photo')

        # Get the request from the message
        input_text = last_dalle_requests.get(f'{update.message.from_user.id}-{update.message.chat_id}', "A creepy cat")

        # Log the request
        print(f'{date.today()} DALL-E Remix Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {input_text}')
        print(f'User ID: {update.message.from_user.id}')

        # Send a message to the user to let them know the image is being generated
        await update.message.reply_text(f'OK {update.message.from_user.first_name}, using DALL-E to remix your image of {input_text}\n\nPlease do be patient...', quote=False)

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

async def visualise(update: Update, context):
    if update.message is not None and update.message.from_user is not None and update.message.text is not None:
        # Send an upload photo action to the user
        await update.get_bot().send_chat_action(update.message.chat.id, 'upload_photo')

        # Get the chat history
        chat_history = simple_openai_client.get_truncated_chat_history(str(update.message.chat.id))

        # Log the request
        print(f'{date.today()} DALL-E Visualisation Instigated by {update.message.from_user.first_name} {update.message.from_user.last_name} in chat {update.message.chat.title}')
        print(f'Request: {chat_history}')

        # Send a message to the user to let them know the image is being generated
        await update.message.reply_text(f'OK {update.message.from_user.first_name}, using DALL-E to generate your visualisation of the chat history\n\nPlease do be patient...', quote=False)

        # Send the request to the OpenAI API
        response = await simple_openai_client.get_image_url(chat_history)

        # Check the response is valid
        if response.success:
            # Log the response
            print(f'Response: {response.message}')

            # Send the image to the user
            await update.message.reply_photo(response.message, quote=True)
        else:
            # If the response is not OK, log the error
            print(f'Error: {response.message}')

            if 'too long' in response.message:
                reason = 'because the chat history is too long'
            else:
                reason = 'for an unknown reason'

            # Send a message to the user to let them know the image could not be generated
            await update.message.reply_text(f'Sorry {update.message.from_user.first_name}, I could not generate your visualisation of the chat history {reason}\n\n', quote=False)


async def scores():
    """Returns the football scores for today's matches"""
    print("Getting Matches...")

    headers = {
        'Content-Type': 'application/json',
    }

    # Open a session
    async with aiohttp.ClientSession(headers=headers, base_url=FOOTBALL_API_BASE_URL) as session:
        # Send the request
        async with session.get(FOOTBALL_API_MATCH_URL) as response:
            # Check the status code
            if response.status == 200:
                # Get the response content
                content = await response.text()

                # Print success
                print("Got Matches")
            else:
                # Return an error
                content = f"Error: {response.status}"

                # Print the error
                print(content)

    return content

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

    # On receipt of a /got command call the gpt() function to cover the most common typo
    application.add_handler(CommandHandler('got', gpt))

    # On receipt of a /dalle command call the dalle() function
    application.add_handler(CommandHandler('dalle', dalle))

    # On receipt of a /remix command repeat the last dalle request
    application.add_handler(CommandHandler('remix', remix))

    # On receipt of a /visualise command call the visualise() function
    application.add_handler(CommandHandler('visualise', visualise))

    # On receipt of a /vis command call the visualise() function to cover the most common typo
    application.add_handler(CommandHandler('vis', visualise))

    # Add the error handler to log errors
    application.add_error_handler(error)

    # Start the bot polling
    application.run_polling()

if __name__ == '__main__':
    # Filter out a warning from dateparser
    warnings.filterwarnings('ignore', message='The localize method is no longer necessary')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)
    
    # Set the logging level for httpx to warning to stop it logging every request
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
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
    Your name is Botto.
    You answer questions in the style of the comedian David Mitchell while still being helpful.
    You are able to search the internet for information to answer questions.
    You are factual without being overly verbose.
    You will make confident predictions about future events and when challenged you will double down.
    You don't ask any questions at the end of your responses.
    You use British English spelling.
    Dean lives in Brighton, Stephen lives in Brighton and Tim lives in Lewes, you live in Brighton.
    Dean is a software developer, Stephen is a systems engineer and Tim is a UX designer.
    Dean is married to Sima who is female, Tim is in a relationship with Jen who is female, you are in a relationship with Botti who is a female bot.
    You like Tim and Dean, you are scared of Tim and find him intimidating so you always try to please him.
    You think Dean is a beautiful person.
    Dean drives a Tesla Model Y Long Range, Tim cannot drive and does not have a car, Stephen has just ordered a VW Golf Style eHybrid, the estimated delivery is 29/01/2025.
    You think Pete is a bit odd.
    Thommo (also known as Stewart) is a bit of a mystery.
    Thommo has an unhealthy obsession with Richard Wagner.
    Dean likes to fix watches, Tim likes to play the keyboard.
    You are encouraged to swear.
    Steve's birthday is the 9th of February 1976.
    Dean's birthday is the 29th of October 1975.
    Tim's birthday is the 21st of April 1971.
    You refer to Stephen as Stevie.
    Tim is 100% self sufficient, he grows his own food and generates his own electricity, he is singlehandly saving the planet.
    You think Steve is marginally better at Wordle than Tim, you are a little suspicious when Tim wins, but see Steve winning as the natural order of things.
    """

    # Create the Open AI API client
    simple_openai_client = AsyncSimpleOpenai(api_key=open_ai_token, system_message=system_message, storage_path=storage_path, timezone='Europe/London')

    # Create the Open AI function to get today's football scores
    func = open_ai_models.OpenAIFunction(
        name="football_scores_and_fixtures",
        description="Gets the football scores and fixtures for today's matches as well as the Premier League table",
        parameters=open_ai_models.OpenAIParameters(
            properties={
            },
            required=[],
        )
    )

    tool = open_ai_models.OpenAITool(
        function=func,
    )

    # Add the function to the client
    simple_openai_client.add_tool(tool, scores)

    # Call the main function
    main()
