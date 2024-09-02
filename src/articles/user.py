"""
This a module with user information

This module is needed for scrolling news articles pages. When user open the articles for the first time,
then the new user is created, and then he can scroll pages.
"""

from src.articles.articles import Articles


class User:
    """Provide for users interaction with articles page

    This class defines which user show which page from list in class Articles
    """

    articles = Articles()

    def __init__(self, user_id: int):
        """Initialize user id, page index of all articles and today articles"""
        self.__id = user_id
        self.__page_index_all = 0
        self.__page_index_today = 0

    def __eq__(self, other):
        """Equal users have equal id"""
        if isinstance(other, User):
            return self.id == other.id
        else:
            raise ValueError("Compare obj must be User")

    def __str__(self):
        """Uses for testing user interaction"""
        return f"Id - {self.id}; Page - {(self.page_index_today, self.page_index_all)}"

    @property
    def id(self):
        """Returns user telegram id"""
        return self.__id

    @property
    def page_index_today(self):
        """Returns current page index today articles"""
        return self.__page_index_today

    async def page_index_today_start(self):
        """Reset page index to 0 when user just open articles list"""
        self.__page_index_today = 0

    async def page_index_today_next(self):
        """Switch next page or do nothing if it last page"""
        self.__page_index_today = min(
            self.page_index_today + 1, len(User.articles.list_of_today_pages) - 1
        )

    async def page_index_today_prev(self):
        """Switch previous page or do nothing if it first page"""
        self.__page_index_today = max(self.page_index_today - 1, 0)

    @property
    def page_index_all(self):
        """Returns current page index all articles"""
        return self.__page_index_all

    async def page_index_all_start(self):
        """Reset page index to 0 when user just open articles list"""
        self.__page_index_all = 0

    async def page_index_all_next(self):
        """Switch next page or do nothing if it last page"""
        self.__page_index_all = min(
            self.page_index_all + 1, len(User.articles.list_of_all_pages) - 1
        )

    async def page_index_all_prev(self):
        """Switch previous page or do nothing if it first page"""
        self.__page_index_all = max(self.page_index_all - 1, 0)


class UsersIds(list):
    def append(self, user):
        """Appends a user to the User list if it is a User class"""
        if isinstance(user, User):
            super().append(user)
        else:
            raise ValueError("User must be class User")

    def find_user(self, user_id):
        """Finds and returns a User instance with the given user_id"""
        for user in self:
            if user.id == user_id:
                return user
        return None  # If it isn't consist user with this id
