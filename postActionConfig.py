from constants import *
from Program import Program

# prompt for ordinary/privileged user

POST_ACTIONS = {
    ORDINARY_QUESTION: {
        "prompt": ORDINARY_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "answer", "vote", "back"],
        "postActionHandlers": {
            "1": Program.postAnswer,
            "answer": Program.postAnswer,
            "2": Program.castVote,
            "vote": Program.castVote,
            "3": BACK_ACTION,
            "back": BACK_ACTION
        }
    },
    ORDINARY_ANSWER: {
        "prompt": ORDINARY_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "2", "vote", "back"],
        "postActionHandlers": {
            "1": Program.castVote,
            "vote": Program.castVote,
            "2": BACK_ACTION,
            "back": BACK_ACTION
        }
    },
    PRIVILEGED_QUESTION: {
        "prompt": PRIVILEGED_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "6", "answer", "vote", "give", "add", "edit", "back"],
        "postActionHandlers": {
            "1": Program.postAnswer,
            "answer": Program.postAnswer,
            "2": Program.castVote,
            "vote": Program.castVote,
            "3": Program.giveBadge,
            "give": Program.giveBadge,
            "4": Program.addTag,
            "add": Program.addTag,
            "5": Program.editPost,
            "edit": Program.editPost,
            "6": BACK_ACTION,
            "back": BACK_ACTION
        }
    },
    PRIVILEGED_ANSWER: {
        "prompt": PRIVILEGED_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "6", "vote", "mark", "give", "add", "edit", "back"],
        "postActionHandlers": {
            "1": Program.castVote,
            "vote": Program.castVote,
            "2": Program.markAccepted,
            "mark": Program.markAccepted,
            "3": Program.giveBadge,
            "give": Program.giveBadge,
            "4": Program.addTag,
            "add": Program.addTag,
            "5": Program.editPost,
            "edit": Program.editPost,
            "6": BACK_ACTION,
            "back": BACK_ACTION
        }
    }
}
