Agent-based chat widget!

Installation:

```
pip install poetry
```
```
poetry install --no-root
```
run frontend:
```
cd widget-frontend; npm i; npm run dev
```
run backend: 
```
poetry shell; python server.py
```


Authentication - to use this app, the user must have google authentication enabled.

```
CLIENT_ID=get_from_google
CLIENT_SECRET=get_from_google
OPENAI_API_KEY=get_from_openai
```

This project creates a chat widget that sits on a desktop of a given website. To access this widget, a user must have a google account because I've used google authentication to create users JIT.

The widget allows the user to interact with a chatbot that can generate and send files to the user. What happens is if the chatbot gets an instruction, it creates a temporary python file that it then executes. So for instance, to generate a csv report, an instruction set to create a python script to accomplish this task is first invoked. Then the executor determines what packages need to be installed, and executes the script in a subprocess. Finally the generated output file (if available) is moved into a directory that is namespaced by the requesting user id. A link with the file location is stored in the db, tied to the user, and available for easy file retrieval. 

Data tables:

users
chats
messages
user_files

Data is effectively stored in a 1->many relationship from the parent user on down. In a scenario where teams may be using this widget, accounts may need to be introduced and user_files may need to be referenced from accounts

