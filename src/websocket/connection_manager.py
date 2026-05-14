class ConnectionManager:

    def __init__(self):

        self.active_connections = {}

    async def connect(
        self,
        room_id,
        websocket
    ):

        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append(
            websocket
        )

        print(f"CONNECTED TO ROOM: {room_id}")

    def disconnect(
        self,
        room_id,
        websocket
    ):

        try:

            self.active_connections[room_id].remove(
                websocket
            )

            print(f"DISCONNECTED FROM ROOM: {room_id}")

        except:
            pass

    async def broadcast(
        self,
        room_id,
        message
    ):

        disconnected = []

        for connection in self.active_connections.get(
            room_id,
            []
        ):

            try:

                await connection.send_text(message)

            except:

                disconnected.append(connection)

        # Remove dead sockets
        for connection in disconnected:

            self.active_connections[room_id].remove(
                connection
            )