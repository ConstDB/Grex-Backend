import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/3/7?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU4MjA2OTk4LjgwOTc5MTgsInR5cGUiOiJhY2Nlc3MifQ.22Nmp4uKa0ng0L5iO84G0PvXKCC6zAehUq_noG8vz8I"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": "okay ka ah",
            "reply_to": 13
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_ws())

