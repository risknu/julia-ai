from __future__ import annotations

from typing import AnyStr

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from juliaai.utility import AbstractUtilityClass
from juliaai.misc import MetaSettings
meta_settings: MetaSettings = MetaSettings


class JuliaAIAPI(AbstractUtilityClass):
    def __init__(self) -> None:
        super().__init__()
        self.__chatbot: ChatBot = ChatBot(meta_settings.agent_name)
        self.__trainer: ListTrainer = ListTrainer(self.__chatbot)

    def response(self, response_context: AnyStr = None) -> AnyStr:
        if not response_context or not isinstance(response_context, str):
            return
        return self.__chatbot.get_response(self._pretty_styler(response_context))

    def train(self, input_data: AnyStr = None, output_data: AnyStr = None) -> bool:
        if (not input_data or not output_data) or not isinstance(input_data, str) or \
              not isinstance(output_data, str):
            return False
        if (input_data == ' ' or input_data == '') or (output_data == ' ' or output_data == ''):
            return False
        self.__trainer.train([
            self._pretty_styler(input_data),
            self._pretty_styler(output_data)])
        return True

    @staticmethod
    def _pretty_styler(string: AnyStr = None) -> AnyStr:
        if not string:
            return
        return string.lower()
    
    @property
    def chatbot_object(self) -> ChatBot:
        return self.__chatbot
    
    @property
    def trainer_object(self) -> ListTrainer:
        return self.__trainer
    
    def __repr__(self) -> str:
        return f"<JuliaAI object class :: {super().__repr__()}>"
