from constants import *
from Program import Program

POST_ACTIONS = {
    ORDINARY_QUESTION: {
        "prompt": ORDINARY_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "answer", "vote"],
        "postActionHandlers": {
            "1": Program.postAnswer,
            "answer": Program.postAnswer,
            "2": Program.castVote,
            "vote": Program.castVote
        }
    },
    ORDINARY_ANSWER: {
        "prompt": ORDINARY_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "vote"],
        "postActionHandlers": {
            "1": Program.castVote,
            "vote": Program.castVote
        }
    },
    PRIVILEGED_QUESTION: {
        "prompt": PRIVILEGED_QUESTION_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "answer", "vote", "give", "add", "edit"],
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
            "edit": Program.editPost
        }
    },
    PRIVILEGED_ANSWER: {
        "prompt": PRIVILEGED_ANSWER_ACTION_PROMPT,
        "validInput": ["1", "2", "3", "4", "5", "vote", "mark", "give", "add", "edit"],
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
            "edit": Program.editPost
        }
    }
}
