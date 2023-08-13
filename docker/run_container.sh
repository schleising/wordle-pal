#!/bin/zsh
docker rm --force wordle-pal
docker run --name wordle-pal -v wordlepal:/storage:rw wordle-pal-image
