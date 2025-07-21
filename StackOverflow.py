#Clarifying quetsions

#Users can post question, post answer and comment on them? yes
#Can they post multiple question and answer ? yes
#Can users vote on questions/answers/comments    yes
#Do we allow edit or delet of the post
#Is reputation or user score based on voting needed?
#Can users tag their questions? if yes Can users search for questions (by keyword/tags)?
#should assign reputation score to users based on their activity and the quality of their contributions. yes
#should handle concurrent access and ensure data consistency. yes

# User: id, email, reputation
#Question: id, title, author, answer, comment. tags, vote, creation date
#Answer: id, vote, content, author, associated question, comments, creation date
#Comment: id, content, answer associated, author, date creation
#Tag: id, name
#Vote: 
#StackOverflow (main): creating user, posting question, tages, votes, answer , commenting, searching for questions and retrieveing questions by tags and users


# ✅ Verbal Design Pitch: Stack Overflow System

# We are designing a simplified version of the Stack Overflow platform with the following core features:

# ✔️ Users:
# - Can create accounts with a username and email
# - Can post multiple questions and answers
# - Can comment on both questions and answers
# - Can vote (upvote/downvote) on questions, answers, and comments
# - Gain reputation based on the votes they receive on their contributions

# ✔️ Questions:
# - Contain a title, body, tags, and metadata (author, date, vote count)
# - Can have multiple answers and comments
# - Are searchable by keyword, tag, or user

# ✔️ Answers:
# - Are linked to a specific question
# - Can be voted on and commented on

# ✔️ Comments:
# - Can be posted on both questions and answers
# - Allow lightweight discussion but do not contribute to reputation

# ✔️ Tags:
# - Allow categorization of questions (e.g., "python", "algorithms")
# - Are searchable and can be used to filter questions

# ✔️ Voting & Reputation:
# - Each user can vote on questions, answers, and comments
# - Upvotes increase the author's reputation
# - Downvotes may decrease it (if implemented)
# - Vote types are modeled via an Enum for +1 (UPVOTE) and -1 (DOWNVOTE)

# ✔️ System Class (StackOverflowSystem):
# - Central manager for users, posts, comments, and tags
# - Handles operations like creating posts, casting votes, searching by tag/user/keyword
# - Maintains in-memory mappings (e.g., user_id → User, tag → questions list)
# - Supports extensibility and modular design

# ✔️ Design Patterns:
# - Observer pattern (optional) could be used for notifications
# - Strategy pattern for future search enhancements (by relevance, recency, etc.)

# This design is intended to be clean, modular, and extensible for future features 
# like notifications, post editing, rate-limiting, moderation tools, etc.

class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
        self.reputation = 0
        self.questions = []
        self.answers = []
        self.comments = []
        
    def ask_questions(self, title, question, content, tag):
        question = Question(self, title, content, tag)
        self.questions.append(question)
        self.update_reputation(5)  # Gain 5 reputation for asking a question
        return question
    
    def answer_question(self, question, content):
        answer = Answer(self, question, content)
        self.answers.append(answer)
        question.add_answer(answer)
        self.update_reputation(10)  # Gain 10 reputation for answering
        return answer
    
    def comment_on(self, commentable, content):
        comment = Comment(self, content)
        self.comments.append(comment)
        commentable.add_comment(comment)
        self.update_reputation(2)  # Gain 2 reputation for commenting
        return comment
    
    def update_reputation(self, value):
        self.reputation += value
        self.reputation = max(0, self.reputation)  # Ensure reputation doesn't go below 0
  
from datetime import datetime

from abc import ABC, abstractmethod

class Votable(ABC):
    @abstractmethod
    def vote(self, user, value):
        pass

    @abstractmethod
    def get_vote_count(self):
        pass
    
from abc import ABC, abstractmethod

class Commentable(ABC):
    @abstractmethod
    def add_comment(self, comment):
        pass

    @abstractmethod
    def get_comments(self):
        pass

from typing import List    

class Vote:
    def __init__(self, user, value):
        self.user = user
        self.value = value      
        
class Tag:
    def __init__(self, name: str):
        self.id = id(self)
        self.name = name
        
class Comment:
    def __init__(self, author, content):
        self.id = id(self)
        self.author = author
        self.content = content
        self.creation_date = datetime.now()

class Question(Votable, Commentable):
    def __init__(self, author, title, content, tag_names):
        self.id = id(self)
        self.author = author
        self.title = title
        self.content = content
        self.creation_date = datetime.now()
        self.answers = []
        self.tags = [Tag(name) for name in tag_names]
        self.votes = []
        self.comments = []
        
    def add_answer(self, answer):
        if answer not in self.answers:
            self.answers.append(answer)
    
    def vote(self, user, value):
        if value not in [-1, 1]:                    # Validate that the vote value is either +1 (upvote) or -1 (downvote)
            raise ValueError("Vote value must be either 1 or -1")
        self.votes = [v for v in self.votes if v.user != user]      # Remove any previous vote from the same user to ensure only one vote per user
        self.votes.append(Vote(user, value))                        # Add the new vote to the list of votes
        self.author.update_reputation(value * 5)  # Update the author's reputation score based on the vote, +5 for upvote, -5 for downvote

    def get_vote_count(self):
        return sum(v.value for v in self.votes) # Calculate total vote count by summing vote values (+1 for upvote, -1 for downvote)

    def add_comment(self, comment):
        self.comments.append(comment)   # Append a new comment to the list of comments for this post

    def get_comments(self) -> List['Comment']:  # Return a shallow copy of the comments list to prevent external modification
        return self.comments.copy()
     
class Answer(Votable, Commentable):
    def __init__(self, author, question, content):
        self.id = id(self)
        self.author = author
        self.question = question
        self.content = content
        self.creation_date = datetime.now()
        self.votes = []
        self.comments = []
        self.is_accepted = False

    def vote(self, user, value):
        if value not in [-1, 1]:
            raise ValueError("Vote value must be either 1 or -1")
        self.votes = [v for v in self.votes if v.user != user]
        self.votes.append(Vote(user, value))
        self.author.update_reputation(value * 10)  # +10 for upvote, -10 for downvote

    def get_vote_count(self) -> int:
        return sum(v.value for v in self.votes)

    def add_comment(self, comment):
        self.comments.append(comment)

    def get_comments(self):
        return self.comments.copy()

    def accept(self):
        if self.is_accepted:
            raise ValueError("This answer is already accepted")
        self.is_accepted = True
        self.author.update_reputation(15)  # +15 reputation for accepted answer
        
from typing import Dict

class StackOverflow:
    def __init__(self):
        # Stores all users by their unique ID
        self.users: Dict[int, User] = {}
        # Stores all questions by their unique ID
        self.questions: Dict[int, Question] = {}
        # Stores all answers by their unique ID
        self.answers: Dict[int, Answer] = {}
        # Stores all tags by their name for quick lookup
        self.tags: Dict[str, Tag] = {}

    def create_user(self, username, email):
        # Create a new user with auto-incremented ID
        user_id = len(self.users) + 1
        user = User(user_id, username, email)
        self.users[user_id] = user
        return user

    def ask_question(self, user, title, content, tags):
        # User asks a question with title, content, and tags
        question = user.ask_question(title, content, tags)
        # Store the question globally by ID
        self.questions[question.id] = question
        # Register any new tags used in this question
        for tag in question.tags:
            self.tags.setdefault(tag.name, tag)
        return question

    def answer_question(self, user, question, content):
        # User answers an existing question
        answer = user.answer_question(question, content)
        # Store the answer globally by ID
        self.answers[answer.id] = answer
        return answer

    def add_comment(self, user, commentable, content):
        # Add a comment to a votable/commentable item (Question or Answer)
        return user.comment_on(commentable, content)

    def vote_question(self, user, question, value):
        # Cast an upvote (+1) or downvote (-1) on a question
        question.vote(user, value)

    def vote_answer(self, user, answer, value):
        # Cast an upvote (+1) or downvote (-1) on an answer
        answer.vote(user, value)

    def accept_answer(self, answer):
        # Mark an answer as the accepted answer
        answer.accept()

    def search_questions(self, query):
        # Simple search: find questions by keyword in title/content or matching tag
        return [q for q in self.questions.values() if query.lower() in q.title.lower() or query.lower() in q.content.lower() or
                any(query.lower() == tag.name.lower() for tag in q.tags)]

    def get_questions_by_user(self, user):
        # Return all questions asked by a specific user
        return user.questions

    def get_user(self, user_id):
        # Retrieve a user by ID
        return self.users.get(user_id)

    def get_question(self, question_id):
        # Retrieve a question by ID
        return self.questions.get(question_id)

    def get_answer(self, answer_id):
        # Retrieve an answer by ID
        return self.answers.get(answer_id)

    def get_tag(self, name: str):
        # Retrieve a tag object by name
        return self.tags.get(name)
