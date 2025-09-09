import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=<token ng user>"
    token = "<Pass a token here if you want to test it>"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": "okay ka ah",
            "reply_to": 3
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_ws())

