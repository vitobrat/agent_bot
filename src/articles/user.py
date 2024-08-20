"""
This a module with user information

This module is needed for scrolling news articles pages. When user open the articles for the first time,
then the new user is created, and then he can scroll pages.
"""
from src.articles.articles import Articles


class User:
    articles = Articles()

    def __init__(self, user_id: int):
        self.__id = user_id
        self.__page_index_all = 0
        self.__page_index_today = 0

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id
        else:
            raise ValueError("Compare obj must be User")

    def __str__(self):
        return f"Id - {self.id}; Page - {(self.page_index_today, self.page_index_all)}"

    @property
    def id(self):
        return self.__id

    @property
    def page_index_today(self):
        return self.__page_index_today

    async def page_index_today_start(self):
        self.__page_index_today = 0

    async def page_index_today_next(self):
        self.__page_index_today = min(self.page_index_today + 1, len(User.articles.list_of_today_pages) - 1)

    async def page_index_today_prev(self):
        self.__page_index_today = max(self.page_index_today - 1, 0)

    @property
    def page_index_all(self):
        return self.__page_index_all

    async def page_index_all_start(self):
        self.__page_index_all = 0

    async def page_index_all_next(self):
        self.__page_index_all = min(self.page_index_all + 1, len(User.articles.list_of_all_pages) - 1)

    async def page_index_all_prev(self):
        self.__page_index_all = max(self.page_index_all - 1, 0)


class UsersIds(list):
    def append(self, user):
        """Appends a user ID to the list if it is an integer."""
        if isinstance(user, User):
            super().append(user)
        else:
            raise ValueError("User ID must be an integer")

    def find_user(self, user_id):
        """Finds and returns a User instance with the given user_id."""
        for user in self:
            if user.id == user_id:
                return user
        return None  # Если пользователь с таким user_id не найден


