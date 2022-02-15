#!/bin/zsh
docker rm --force wordle-pal
docker run --name wordle-pal wordle-pal-image
