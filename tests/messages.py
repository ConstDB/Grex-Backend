import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTgyMjUxODQuMjMzMzM3NiwidHlwZSI6ImFjY2VzcyJ9.VdAfW1uliMOuiU0qcourhyuJ3BEOdIgTjU0FL2e7ft4"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": "Hello self",
            "reply_to": None
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_ws())

