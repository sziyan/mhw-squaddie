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

The following **squad** management commands are available:
New members to chat are automatically added to this list.
- /pendingsquad
- /invitedsquad <name>

The following *fun* commands are available:
- /youtube <search terms>

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
