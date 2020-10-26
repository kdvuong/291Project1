ACTION_OPTIONS = """-----------------------------------
Choose the following option:
-----------------------------------
POST (post a question)
SEARCH (search for a post)
LOGOUT (log out)
------------------------------------
What do you want to do? """

ORDINARY_QUESTION = "ORDINARY_QUESTION"
ORDINARY_ANSWER = "ORDINARY_ANSWER"
PRIVILEGED_QUESTION = "PRIVILEGED_QUESTION"
PRIVILEGED_ANSWER = "PRIVILEGED_ANSWER"

ORDINARY_QUESTION_ACTION_PROMPT = """
Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post

Choose an action (number or text): """

ORDINARY_ANSWER_ACTION_PROMPT = """
Available actions:
1. Vote - cast vote for a post

Choose an action (number or text): """

PRIVILEGED_QUESTION_ACTION_PROMPT = """
Available actions:
1. Answer - post answer to a question
2. Vote - cast vote for a post
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post

Choose an action (number or text): """

PRIVILEGED_ANSWER_ACTION_PROMPT = """
Available actions:
1. Vote - cast vote for a post
2. Mark - mark an answer as accepted
3. Give - give a badge to a poster
4. Add - add tags to a post
5. Edit - edit the title and/or the body of the post

Choose an action (number or text): """

EDIT_ACTION_PROMPT = """
Available actions:
1. Edit both title and body of the post
2. Edit the title only
3. Edit the body only

Choose an action (number): """

SEARCH_SUCCESS_ACTION_PROMPT = """
Available actions:
POSTID (Enter a post id to select it)
NEXT (View next page)
PREV (View previous page)
BACK (Back to main menu)

Choose an action (text): """