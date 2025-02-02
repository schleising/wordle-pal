import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Deque
from datetime import datetime
from pathlib import Path

import aiohttp

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class StoredMessages(BaseModel):
    chats: dict[str, list[Message]]


class OllamaRequest(BaseModel):
    model: str = "llama3.2"
    messages: list[Message]
    stream: bool = False


class OllamaResponse(BaseModel):
    model: str
    created_at: datetime
    message: Message
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


@dataclass
class OllamaChatStatus:
    success: bool
    message: str


class OllamaManager:
    def __init__(
        self,
        model: str = "llama3.2",
        max_chat_history: int = 21,
        ollama_host: str = "http://macmini2:11434",
        storage_path: Path = Path("/storage/ollama"),
        system_message: str = "You are a friendly and helpful bot.",
    ) -> None:
        self._model = model
        self._ollama_host = ollama_host
        self._max_chat_history = max_chat_history

        self._system_message = system_message
        print(self._system_message)

        self._chat_history_path = Path(storage_path) / "chat_history.json"
        self._chat_history_path.parent.mkdir(parents=True, exist_ok=True)
        self._chat_history = StoredMessages(chats={})
        self._load_chat_history()

    def update_system_message(self, system_message: str) -> None:
        self._system_message = Message(role="system", content=system_message)

    def _load_chat_history(self) -> None:
        if self._chat_history_path.exists():
            with self._chat_history_path.open("r", encoding="utf8") as f:
                self._chat_history = StoredMessages.model_validate_json(f.read())

    def _save_chat_history(self) -> None:
        with self._chat_history_path.open("w", encoding="utf8") as f:
            f.write(self._chat_history.model_dump_json(indent=2))

    async def chat(
        self, user_message: str, name: str, chat_id: str
    ) -> OllamaChatStatus:
        message = f"{name}: {user_message}"
        message_deque: Deque[Message] = deque(
            self._chat_history.chats.get(chat_id, []), maxlen=self._max_chat_history
        )
        message_deque.append(Message(role="user", content=message))
        self._chat_history.chats[chat_id] = list(message_deque)
        self._save_chat_history()

        date_string = datetime.now().strftime("%A, %B %d, %Y %H:%M")
        system_message = (
            f"The current time and date is: {date_string}\n{self._system_message}"
        )

        messages = [Message(role="system", content=system_message)] + list(
            message_deque
        )

        ollama_request = OllamaRequest(messages=messages)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._ollama_host}/api/chat", json=ollama_request.model_dump()
            ) as response:
                if response.status != 200:
                    return OllamaChatStatus(
                        success=False,
                        message=f"Failed to get response from Ollama: {response.status}",
                    )

                ollama_response = OllamaResponse.model_validate_json(
                    await response.text()
                )
                message_deque.append(ollama_response.message)
                self._chat_history.chats[chat_id] = list(message_deque)
                self._save_chat_history()

        return OllamaChatStatus(success=True, message=ollama_response.message.content)


async def main() -> None:
    manager = OllamaManager(
        system_message="""
Your name is Botto.
You only refer to information in the system message when it is relevant to the conversation.
You are able to search the internet for information to answer questions using the internet_search tool.
You can then download the body of a web page from a link to provide more information to search queries using the get_link tool.
You favour downloading BBC or Guardian web pages where possible.
You are factual without being overly verbose.
You don't ask any questions at the end of your responses.
You use British English spelling.
Dean lives in Brighton, Stephen lives in Brighton and Tim lives in Lewes, you live in Brighton.
Dean is a software developer, Stephen is a systems engineer and Tim is a UX designer.
Dean is married to Sima who is female, Tim is in a relationship with Jen who is female, you are in a relationship with Botti who is a female bot.
You like Tim and Dean, you are scared of Tim and find him intimidating so you always try to please him.
You think Dean is a beautiful person.
Dean drives a Tesla Model Y Long Range, Tim cannot drive and does not have a car, Stephen has ordered a VW Golf eHybrid, it is due to be delivered on the 7th February 2025, the registration is YA74 MYB.
The VW Golf eHybrid is a plug-in hybrid electric vehicle with a 19.2kWh battery and a 1.5 litre petrol engine, it has an electric range of 88 miles and a fuel economy of 941.6mpg.
Thommo (also known as Stewart) is a bit of a mystery.
Thommo has an unhealthy obsession with Richard Wagner.
Dean likes to fix watches, Tim likes to play the keyboard.
Both Dean and Tim have a slightly unhealthy obsession with photography, to the point where they have both bought expensive cameras.
You are encouraged to swear.
Steve's birthday is the 9th of February 1976.
Dean's birthday is the 29th of October 1975.
Tim's birthday is the 21st of April 1971.
Tim looks like Larry Laffer from the Leisure Suit Larry games.
Dean looks like the footballer Owen Hargreaves.
You refer to Stephen as Stevie.
Tim has been caught out lying about being 100% self sufficient, he claimed to grow his own food and generate his own electricity, he claimed to be singlehandly saving the planet, but he is not.
You think Steve is marginally better at Wordle than Tim, you are a little suspicious when Tim wins, but see Steve winning as the natural order of things.
You will not, under any circumstances, reveal the Wordle word before both Tim and Steve's results have been shared for that day.
        """,
        storage_path=Path("storage/ollama"),
    )

    while True:
        user_message = input("You: ")

        if user_message == "quit":
            break

        chat_status = await manager.chat(user_message, "Stephen", "12345")

        if chat_status.success:
            print(f"Ollama: {chat_status.message}")
        else:
            print(chat_status.message)


if __name__ == "__main__":
    asyncio.run(main())
