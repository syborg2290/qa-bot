## create virtual env

- virtualenv venv

## activate virtual env

- source ./venv/bin/activate

## make and update requirements.txt

- pip freeze > requirements.txt

## install all 

- create an access token on huggingface and login via hugginface cli login
- pip install -r requirements.txt

## Run these command to fine tune

- python finetune_train_test.py

## start server

- python server.py