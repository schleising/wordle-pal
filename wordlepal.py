from datetime import date, timedelta
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
            outputFile.write(f'{words.guessNumberString}\n')

        # Write out the number of guesses it took today
        with open(Path('guessesToday.txt'), 'w', encoding='utf-8') as outputFile:
            outputFile.write(f'{words.guessNumberString}\n')

        # Open the history file and get the new average score
        with open('history.txt', 'r', encoding='utf-8') as inputFile:
            # Create a list for the guess number history
            guessNumberHistory = [int(line) for line in inputFile]

        # Calculate the average score
        averageScore = sum(guessNumberHistory) / len(guessNumberHistory)

        # Output the average score
        print()
        print(f'Average Score: {averageScore:.2f}')
        print('===================')

        # Get the counts of each score
        scoreCounts = Counter(guessNumberHistory)

        # Update the readme file
        with open('README.md', 'w') as readmeFile:
            readmeFile.write('[![Python application](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml/badge.svg)](https://github.com/schleising/wordle-pal/actions/workflows/python-app.yml)\n')
            readmeFile.write('# wordle-pal\n')
            readmeFile.write('## Help with Wordle words\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n\n')
            readmeFile.write(f"## Got today's word in {words.guessNumberString} attempts</br>\n")

            for guessGraphic in words.guessHistory:
                readmeFile.write(f'{"".join(guessGraphic)}\\\n')
    
            readmeFile.write('</br>\n')

            readmeFile.write(f'## Average Number of Guesses: {averageScore:.2f}</br>\n')

            readmeFile.write('## Guess Statistics</br>\n')

            for count in range(Constants.MAX_GUESSES):
                readmeFile.write(f'    {count+1}: {scoreCounts.get(count+1, 0)}\n')

            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
            readmeFile.write('</br>\n')
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

            outputFile.write('===============\n')
            outputFile.write(f'Wordle {words.dayNumber} {words.guessNumberString}/6\n')
            outputFile.write('\n')

            # Output a Wordle like graphic
            for guessGraphic in words.guessHistory:
                outputFile.write(f"{''.join(guessGraphic)}\n")

            currentDate = currentDate + timedelta(days=1)

def GenerateDistGraphic() -> Path:
    with open(Path('history.txt'), 'r', encoding='utf-8') as historyFile:
        # Create a list for the guess number history
        guessNumberHistory = [int(line) for line in historyFile]

    with open(Path('guessesToday.txt'), 'r', encoding='utf-8') as guessesFile:
        # Get today's guess number
        guessNumberToday = int(guessesFile.read().strip())

    # Count the number of guesses
    guessNumberCounter = Counter(guessNumberHistory)

    # Turn this counter into a scores dict
    scores = {count+1: guessNumberCounter.get(count+1, 0) for count in range(Constants.MAX_GUESSES)}

    # Create a list to store the individual images which will make up the full image
    imageList = []

    # Create fonts for the text on the image
    textFont = ImageFont.truetype('Roboto/Roboto-Black.ttf', 45)
    scoreFont = ImageFont.truetype('Roboto/Roboto-Regular.ttf', 45)

    # Create an image for the guess distribution text and get the drawing context
    gdImage = Image.new('RGB', Constants.GUESS_DISTRIBUTION_SIZE, 'white')
    gdDraw = ImageDraw.Draw(gdImage)

    # Set the text anchor position to the centre of the image
    gdAnchorPos = tuple(dim // 2 for dim in Constants.GUESS_DISTRIBUTION_SIZE)

    # Draw the text on the image in the center of the image space
    gdDraw.text(gdAnchorPos, 'GUESS DISTRIBUTION', fill='black', anchor='mm', font=textFont)

    # Append this image to the list
    imageList.append(gdImage)

    # Get the maximum score so we know how long to make the bars
    maximumCount = max(scores.values())

    # Loop through the scores creating a bar image for each
    for score, count in scores.items():
        # Create the bar image and get the draw context
        barImage = Image.new('RGB', Constants.BAR_SCORE_SIZE, 'white')
        barDraw = ImageDraw.Draw(barImage)

        # Get the score anchor position
        scoreAnchorPos = tuple(dim // 2 for dim in Constants.SCORE_SIZE)

        # Draw the score on the bar image
        barDraw.text(scoreAnchorPos, str(score), fill='black', anchor='mm', font=scoreFont)

        # Only draw the bar and count of that score if the score isn't 0
        if count != 0:
            # Calculate the length of the bar based on the ratio of count to maximum count
            barLength = (Constants.BAR_SIZE[0] * count / maximumCount) - 5

            # Draw the rectangle in grey or green if it matches today's score
            fillColour = 'mediumseagreen' if score == guessNumberToday else 'grey'
            barDraw.rectangle((50, 5, barLength + Constants.SCORE_SIZE[0], Constants.BAR_SIZE[1] - 5), fill=fillColour)

            # Get the count for this score as a string
            countText = str(count)

            # Work out the length of the resultant string
            countLength = scoreFont.getlength(countText)

            # Using this length value, work out where it should be placed
            countAnchorPos = (barLength + Constants.SCORE_SIZE[0] - countLength // 2 - 10, Constants.BAR_SIZE[1] // 2)

            # Draw the count onto the right side of the  bar
            barDraw.text(countAnchorPos, countText, fill='white', anchor='mm', font=scoreFont)

        # Add this image to the list
        imageList.append(barImage)

    # Create a full image to paste the individual images into
    fullImage = Image.new('RGB', Constants.FULL_IMAGE_SIZE, 'white')

    # Get the height each image can take up and the halfway point
    imageBoxHeight = Constants.FULL_IMAGE_SIZE[1] // len(imageList)
    imageBoxCentrePoint = imageBoxHeight // 2

    # Loop through the images in the list
    for count, image in enumerate(imageList):
        # Work out the left, top, right and bottom points of the image to be pasted in
        imageLeft = (fullImage.size[0] - image.size[0]) // 2
        imageTop = (count * imageBoxHeight) + imageBoxCentrePoint - (image.size[1] // 2)
        imageRight = imageLeft + image.size[0]
        imageBottom = imageTop + image.size[1]

        # Paste the image in
        fullImage.paste(image, (imageLeft, imageTop, imageRight, imageBottom))

    # Save the image
    filename = Path('GuessDistribution.png')
    fullImage.save(filename, 'PNG')

    # Return the image as bytes
    return filename

if __name__ == '__main__':
    RunGame(downloadWords=True, writeFiles=True, verbose=True)

    # RunCompleteGame()
