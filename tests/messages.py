import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTg4NjQ3ODEuOTQ0Njg1LCJ0eXBlIjoiYWNjZXNzIn0.ZeCKM2LwLIEINay51PLQkD5dSBhCzNnrYydaHPbS0Js"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": {
                "text": "Hello self"
            },
            "reply_to": None
        }))

        response =  await ws.recv()
        print(f"Recieved: {response} ")

async def test_message_attachment():
    uri = "ws://127.0.0.1:8000/workspace/1/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTg4NjQ3ODEuOTQ0Njg1LCJ0eXBlIjoiYWNjZXNzIn0.ZeCKM2LwLIEINay51PLQkD5dSBhCzNnrYydaHPbS0Js"
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

# with open('./mock_messages.json', "r") as file:
#     messages = json.load(file)

asyncio.run(test_message_attachment())
asyncio.run(test_ws())


