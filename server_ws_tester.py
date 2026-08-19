import asyncio

import websockets

server_uuid = "c697c5fb-3937-413b-9627-871c8971db27"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzg3MjExNjEyfQ.5bzF5ed93JxPhf3FnX6FLRFLTC-d9UsmCLtVheuef2M"


async def main() -> None:
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}

    uri = f"ws://127.0.0.1:8080/servers/{server_uuid}/ws"

    async with websockets.connect(uri, additional_headers=headers) as client:
        while True:
            message = await client.recv(decode=True)
            print(message)


if __name__ == "__main__":
    asyncio.run(main())
