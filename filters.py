from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config

class IsOwnerFilter(BoundFilter):
    """
    Пользовательский фильтр "is_owner".
    """
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def check(self, message: types.Message):
        return message.from_user.id == config.BOT_OWNER

class IsAdminFilter(BoundFilter):
    """
    Фильтр, проверяющий наличие прав администратора
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin


class MemberCanRestrictFilter(BoundFilter):
    """
    Фильтр, который проверяет способность элемента ограничивать
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        # Я не знаю почему, но telegram считает, что если пользователь является создателем чата, он не может ограничить доступ к нему
        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict