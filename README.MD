## MHW-Squaddie Telegram Bot

This bot serves the purpose of organizing hunts in telegram groups, most importantly, to organize siege hunts.

Siege organization uses MongoDB to store information.

The following **siege** commands are available:
- /setsiege <time>
- /joinsiege <siege id> `defaults to 1 if no parameter is input`
- /leavesiege <siege id> `defaults to 1 if no parameter is input`
- /checksiege

The following **session** commands are available:
- /addsession <session id>
- /session
- /deletesession

The following **event** comands are available:
- /addevent
- /checkevent
- /deleteevent
- /joinevent

Additional commands below:
- /admin

Reddit links are also replied with a summary of 100 words.

# Installing
Before installing, make sure to create `config.py` and place it in the same folder as `app.py`

```python
class Config:
	API_KEY = 'youtube api_key'
    	client_id = 'reddit client_id'
    	client_secret = 'reddit_client_secret'
    	host = "mongodb connection"
	token = 'telegram token'
```

### MHW Discord Bot

This bot serves the purpose of organizing sieges/quests and sieges into different discord text channels.

The following commands are available:

- /addlfg
- /addsession
- /help
- /card
- /showcard