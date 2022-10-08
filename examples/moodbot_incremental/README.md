# Moodbot Incremental

Read Moodbot Readme for readme on moodbot

# Running Model
incremental RASA only works with NLU...
when running it from a python file call it this way

```
from rasa.core.agent import Agent
agent = Agent.load("examples/moodbot/models")
incremental_parse_message(("What is the weather two","ADD"))
incremental_parse_message(("two","REVOKE"))
incremental_parse_message(("today","ADD"))
```

**OR**

Inside terminal
```
rasa shell nlu
```