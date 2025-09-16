import asyncio
import websockets
import json



async def test_ws(data: dict):
    uri = f"ws://127.0.0.1:8000/workspace/{data["workspace_id"]}/{data["user_id"]}?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZHJpY2hkYXJyZW5zYW50dXlvQGdtYWlsLmNvbSIsImV4cCI6MTc1ODAyNjI5MS44NzM1MTc1LCJ0eXBlIjoiYWNjZXNzIn0.68KziOgc8o8sVaao7jyKMbV_p15pivooLY_elb-ddD8"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type":"text",
            "content": data["message"],
            "reply_to": None
        }))

        response =  await ws.recv()

with open('./mock_messages.json', "r") as file:
    messages = json.load(file)

for message in messages:
    asyncio.run(test_ws(message))