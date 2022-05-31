#!/bin/bash
source .env
curl -c cookie-jar.txt -X POST -H 'Content-Type: application/json' --data "{\"email\": \"$email\", \"password\": \"$password\"}" https://members-ng.iracing.com/auth