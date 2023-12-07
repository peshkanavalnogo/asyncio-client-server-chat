import asyncio
import aioconsole
import tkinter as tk
from tkinter import scrolledtext


async def tk_main(root):
    while True:
        root.update()
        await asyncio.sleep(0.05)

async def send_message(writer, message):
    writer.write(message.encode())
    await writer.drain()
    text_box.insert(tk.END, "\n" + message)

async def receive_messages(reader):
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        text_box.insert(tk.END, "\n" + message)
        print(message)

async def get_username(reader, writer, username):
    # Receive and print the prompt for entering a username
    prompt = await reader.read(100)
    print(prompt.decode())



    # Get the username from the user using aioconsole
    #username = await aioconsole.ainput()
    await send_message(writer, username)

    #return username

async def main(root):
    global writer
    global reader
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    tkmain = asyncio.ensure_future(tk_main(root))
    await receive_messages(reader)
    await asyncio.sleep(5)

    try:
        # Get the username from the user
        #username = await get_username(reader, writer)

        # Start tasks to continuously receive and process messages from the server
        asyncio.create_task(receive_messages(reader))
        await asyncio.sleep(1)
        await send_message(writer, "/join general")
        while True:
            message = await aioconsole.ainput()
            if message.lower() == 'exit':
                break

            # Send message to the server
            await send_message(writer, message)

    finally:
        writer.close()
        await writer.wait_closed()

def click():
    asyncio.create_task(send())



async def send():
    message = n.get()
    await send_message(writer, message)
    n.set("")



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    n = tk.StringVar()
    text_box = scrolledtext.ScrolledText(root,wrap=tk.WORD, width=75, height=36)
    send_entry = tk.Entry(root, textvariable=n)
    buttn = tk.Button(root, command=click, text="Enter message")
    send_entry.grid(row = 10, column=1)
    buttn.grid(row=11, column=1)

    text_box.grid(row=4, column=1)
    asyncio.run(main(root))
