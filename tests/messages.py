import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTc1ODA1OTguMTM2MTM3NywidHlwZSI6ImFjY2VzcyJ9.ODlrPKd4bvtbPAEccbgxA89a0mkHr-BDpUoDr1CBuKw"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": "okay ka ah",
            "reply_to": None
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_ws())

