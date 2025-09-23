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

async def test_message_attachment():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTg2OTAxNDguMzQxMTQ1OCwidHlwZSI6ImFjY2VzcyJ9.afup0tiE79Gs7784nkPqiwFKU2sJ5tmSQuFx46dMZes"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"attachment",
            "content": {
                "file_name": "test.docx",
                "file_url": "test.com",
                "file_type": "file",
                "file_size": 23.4 
            },
            "reply_to": None
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")


asyncio.run(test_message_attachment())

