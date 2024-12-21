FROM python:3-alpine
ENV PYTHONUNBUFFERED 1

# Install the build tools
# RUN apk update && apk add git

# Make the code directory
WORKDIR /code

# Install requirements for the covid charts script
COPY ./requirements.txt /code/
RUN pip install -r ./requirements.txt

# Run a command to ensure the container does not exit
CMD [ "python", "wordlepalbot.py" ]
