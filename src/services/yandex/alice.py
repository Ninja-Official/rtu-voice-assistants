import collections
import logging

from abc import ABC, abstractmethod
from aiohttp import ClientSession
from functools import lru_cache

from fastapi import Depends
from typing import Union, Any, Awaitable
from starlette.requests import Request

from src.core.session import get_session
from src.assistants.yandex.request import AliceRequest
from src.core.yandex.scenes import Welcome, SCENES, WelcomeDefault
from src.core.yandex.state import STATE_REQUEST_KEY
from src.crud.user import create_user, get_user
from src.database.database import get_db, Session

logger = logging.getLogger(__name__)


class VoiceAssistantServiceBase(ABC):

    @abstractmethod
    def parse_request_and_routing(self, *args, **kwargs) -> Union[Any, Awaitable[Any]]:
        ...


class AliceVoiceAssistantService(VoiceAssistantServiceBase):
    def __init__(self, session: ClientSession, db: Session) -> None:
        self.session = session
        self.db = db

    async def parse_request_and_routing(self, request: Request) -> dict[str, Any]:

        event = await request.json()

        request = AliceRequest(request_body=event, session=self.session, db=self.db)
        current_scene_id = event.get('state', {}).get(
            STATE_REQUEST_KEY, {}).get('scene')

        if current_scene_id is None:

            if request.user_id != '':
                user_id = request.user_id

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                else:

                    user = {
                        "user_id": user_id,
                        "group": "",
                        "platform": "YANDEX"
                    }

                    await create_user(user, self.db)
                    return await Welcome().reply(request)

            elif request.application_id != '':
                user_id = request.application_id

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                else:
                    user = {
                        "user_id": user_id,
                        "group": "",
                        "platform": "YANDEX"
                    }

                    await create_user(user, self.db)
                    return await Welcome().reply(request)
                    
        current_scene = SCENES.get(current_scene_id, Welcome)()
        next_scene = current_scene.move(request)

        if next_scene is not None:
            return await next_scene.reply(request)
        else:
            return await current_scene.fallback(request)


@lru_cache()
async def get_alice_voice_assistant_service(session: Awaitable[ClientSession] = Depends(get_session), db: Session = Depends(get_db)) -> AliceVoiceAssistantService:

    if isinstance(session, collections.abc.Awaitable):
        session = await session

    return AliceVoiceAssistantService(session=session, db=db)
