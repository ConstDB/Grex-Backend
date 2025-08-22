import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/1/10"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": """
            
            The Fool that doesn't belong to this era

            The great ruler above the gray fog

            King of Yellow and Black who wills good luck!
            
            """,
            "reply_to": None

        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_ws())
# async def test_ws():
#     async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
#         msg = await ws.recv()
#         print("✅ received:", msg)

# asyncio.run(test_ws())