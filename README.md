```
   __________  ______
  / ____/ __ \/_  __/
 / / __/ /_/ / / /   
/ /_/ / ____/ / /    
\____/_/     /_/     
                     
   ________  ______  ____________       ______  ____________________ 
  / ____/ / / / __ \/ ___/_  __/ |     / / __ \/  _/_  __/ ____/ __ \
 / / __/ /_/ / / / /\__ \ / /  | | /| / / /_/ // /  / / / __/ / /_/ /
/ /_/ / __  / /_/ /___/ // /   | |/ |/ / _, _// /  / / / /___/ _, _/ 
\____/_/ /_/\____//____//_/    |__/|__/_/ |_/___/ /_/ /_____/_/ |_|  

```


## Overview

This uses OpenAI's GPT LLM to write git commit summaries

        
## Setup

      pip install gpt-ghostwriter
      export OPENAI_API_KEY=xxxxxxxxxxxxxxxxxx

### Usage        

      git commit -m "$(ghostwriter)"

### Example

      $ echo "test" > test.txt
      $ git add test.txt
      $ ghostwriter
      "Adds a test.txt file to repo"

