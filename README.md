A simple Slack bot which can get ids, fetch web pages and run shell commands.

Config file format:
 - bot: The Slack bot's token
 - prefix: The prefix all commands need to start with
 - commands: A dictionary of commands:
   - key: The trigger to run the command with
   - type: one of "get_id", "read_web" or "run_cmd"
   - url: only when type is "read_web". The url to fetch
   - cmd: only when type is "run_cmd". The command to run.
   - display_output: only when type is "run_cmd". Whether to show stdout and stderr of the command

   - reply1: What to reply the message with
   - complete: The message to show on command completion
   - acl1: A list of Slack user ids who can run the command. If not present, run the command without further checks
   - acl2: A list of Slack user ids who can verify the command. If not present, run the command without further checks
   - trigger2: The trigger for acl2 to be checked
   - reply2: The message to show when acl2 has been verified
   - timeout: How long to wait before cancelling the command waiting for a second person


Installing:

This bot uses Python 3.6.
Create a virtualenv and install with `pip install -r requirements.txt`.

Run with `python main.py` in the installation directory.