START_ACTION_PROMPT = """1. LOGIN
2. REGISTER
3. EXIT

What do you want to do? (number or text): """

ACTION_OPTIONS = """-----------------------------------
Choose the following option:
-----------------------------------
1. POST (post a question)
2. SEARCH (search for a post)
3. LOGOUT (log out)
------------------------------------
What do you want to do? (number or text): """

ORDINARY_QUESTION = "ORDINARY_QUESTION"
ORDINARY_ANSWER = "ORDINARY_ANSWER"
PRIVILEGED_QUESTION = "PRIVILEGED_QUESTION"
PRIVILEGED_ANSWER = "PRIVILEGED_ANSWER"

ORDINARY_QUESTION_ACTION_PROMPT = """
Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post
3. Back - back to search screen

Choose an action (number or text): """

ORDINARY_ANSWER_ACTION_PROMPT = """
Available actions:
1. Vote - cast vote for a post
2. Back - back to search screen

Choose an action (number or text): """

PRIVILEGED_QUESTION_ACTION_PROMPT = """
Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post
6. Back - back to search screen

Choose an action (number or text): """

PRIVILEGED_ANSWER_ACTION_PROMPT = """
Available actions:
1. Vote - cast vote for a post
2. Mark - mark an answer as accepted
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post
6. Back - back to search screen

Choose an action (number or text): """

BACK_ACTION = "BACK_ACTION"

EDIT_ACTION_PROMPT = """
Available actions:
1. Edit both title and body of the post
2. Edit the title only
3. Edit the body only

Choose an action (number): """

NEXT_PAGE_PROMPT = "\nNEXT (View next page)"
PREV_PAGE_PROMPT = "\nPREV (View previous page)"

SEARCH_SUCCESS_ACTION_PROMPT = """
Available actions:
POSTID (Enter a post id to select it){next}{prev}
BACK (Back to main menu)

Choose an action (text): """
