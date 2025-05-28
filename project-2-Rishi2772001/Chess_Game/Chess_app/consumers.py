import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Game
from .utils import move_piece

UserModel = get_user_model()


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"game_{self.game_id}"
        self.user = self.scope["user"]
        game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        players = await database_sync_to_async(lambda: (game.player1_id, game.player2_id))()
        if self.user.id not in players:
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action", "move")
        if action == "move":
            result = await self.process_move(data.get("move"))
            if result["valid"]:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "game_update", "message": {"type": "move", "data": result}},
                )
            else:
                await self.send(text_data=json.dumps({"type": "error", "message": result["message"]}))
        elif action == "resign":
            result = await self.process_resign()
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "game_update", "message": {"type": "resign", "data": result}},
            )

    async def process_move(self, move_input):
        game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        return await database_sync_to_async(move_piece)(self.user, game, move_input)

    async def process_resign(self):
        game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        winner = await database_sync_to_async(lambda: game.player2 if game.player1_id == self.user.id else game.player1)()
        game.status = "finished"
        game.winner = winner
        game.result = "1-0" if winner.id == game.player1_id else "0-1"
        await database_sync_to_async(game.save)()
        return {
            "valid": True,
            "message": f"{self.user.username} has resigned. {winner.username} wins.",
            "status": game.status,
            "winner": winner.username,
            "result": game.result,
        }

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        self.user_group = f"user_{self.user.id}"
        self.lobby_group = "lobby"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add(self.lobby_group, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.lobby_group,
            {"type": "presence_update", "action": "online", "user_id": self.user.id, "username": self.user.username},
        )
        online_users = await self._online_users()
        await self.send(text_data=json.dumps({"type": "presence_snapshot", "online": online_users}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)
        await self.channel_layer.group_discard(self.lobby_group, self.channel_name)
        await self.channel_layer.group_send(
            self.lobby_group, {"type": "presence_update", "action": "offline", "user_id": self.user.id}
        )

    async def receive(self, text_data):
        pass

    async def notify(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _online_users(self):
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now())
        ids = [int(s.get_decoded().get("_auth_user_id")) for s in active_sessions if s.get_decoded().get("_auth_user_id")]
        return list(UserModel.objects.filter(id__in=ids).values("id", "username"))
