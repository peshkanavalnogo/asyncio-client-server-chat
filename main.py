import asyncio



class ChatServer:
    def __init__(self):
        self.clients = set()
        self.rooms = dict()

    def get_keys_by_value(my_dict, target_value):
        return [key for key, value in my_dict.items() if value == target_value]


    async def handle_client(self, reader, writer):
        # Get the client's address
        address = writer.get_extra_info('peername')
        print(f"New connection from {address}")

        # Get the username from the client using aioconsole
        await self.send_message(writer, "Enter your username: ")
        username = (await reader.read(100)).decode().strip()
        self.clients.add((reader, writer, username))

        # Send a welcome message to the new client
        await self.send_message(writer, f"Welcome, {username}!")

        try:
            while True:
                # Read data from the client
                data = await reader.read(100)
                if not data:
                    break

                message = data.decode()
                print(f"Received message from {username}: {message}")

                # Broadcast the message to all clients except the sender
                await self.handle_message(username, message, writer)

        except asyncio.CancelledError:
            pass
        finally:
            # Remove the client from the set
            self.clients.remove((reader, writer, username))
            await self.broadcast(f"{username} has left the chat(", writer)
            writer.close()
            await writer.wait_closed()
            print(f"Connection from {address} closed")

    async def handle_message(self, username, message, writer):
        if message.startswith("/join"):
            room_name = message.split()[1]
            await self.join_room(username, room_name, writer)
        elif message.startswith("/leave"):
            room_name = message.split()[1]
            await self.left_room(username, room_name, writer)
        elif message.startswith("/pm"):
            tmp = message.split()
            usernamee = ''
            mes = ''
            print(tmp)
            for i in tmp:
                if i != "/pm":
                    usernamee = i
                    break
            n = 0
            for i in tmp:
                n += 1
                if n > 2:
                    mes += i + " "
            await self.send_pm(usernamee, mes, writer)


        else:
            await self.broadcast(f"{username}: {message}", writer)

    async def send_pm(self, username, message, writer):
        for _, client_writer, usernamemb in self.clients:
            print(usernamemb)
            if str(usernamemb) == str(username):
                print("succ")
                await self.send_message(client_writer, f"pm from {username}: " + message)
                break
            

    async def left_room(self, username, room_name, writer):
        if room_name not in self.rooms:
            await self.send_message(writer, "There is no room with this name.")
        else:
            for user in self.rooms[room_name]:
                if user == writer:
                    await self.broadcast(f"{username} has left the room {room_name}(", writer)
                    self.rooms[room_name].remove(writer)
                    break


    async def join_room(self, username, room_name, writer):
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        self.rooms[room_name].add(writer)
        print(self.rooms)

        await self.broadcast(f"{username} has joined room {room_name}.\n", writer)

        for room in self.rooms.keys():
            if room != room_name:
                await self.left_room(username, room, writer)

    async def broadcast(self, message, sender):
        # Send the message to all clients except the sender
        for _, client_writer, _ in self.clients:
            for room in self.rooms.keys():
                user_in_room = list(self.rooms[room])
                if client_writer != sender and client_writer in user_in_room and sender in user_in_room:
                    try:
                        await self.send_message(client_writer, message)
                    except asyncio.CancelledError:
                        pass

    async def send_message(self, writer, message):
        writer.write(message.encode())
        await writer.drain()

    async def start_server(self, host, port):
        server = await asyncio.start_server(
            self.handle_client, host, port
        )
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    chat_server = ChatServer()
    asyncio.run(chat_server.start_server('127.0.0.1', 8888))
