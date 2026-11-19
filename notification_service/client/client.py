import asyncio
import json
import sys

import websockets


async def run(user_id: str, url: str) -> None:
    full_url = f"{url}?user_id={user_id}"

    while True:
        try:
            async with websockets.connect(full_url) as ws:
                print(f"connected: {full_url}")

                async for raw in ws:
                    if raw == "pong":
                        continue

                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        print(f"raw message: {raw}")
                        continue

                    kind = data.get("kind")

                    if kind == "hello":
                        print(f"handshake ok (user_id={data.get('user_id')})")
                        continue

                    if kind == "notification":
                        print()
                        print(f"[{data.get('created_at', '')}] {data.get('title', '')}")
                        print(data.get("body", ""))
                        meta = []
                        if data.get("event_type"):
                            meta.append(data["event_type"])
                        if data.get("deal_id"):
                            meta.append(f"deal_id={data['deal_id']}")
                        if data.get("activity_id"):
                            meta.append(f"activity_id={data['activity_id']}")
                        if meta:
                            print(" | ".join(meta))
                        print()

        except (websockets.ConnectionClosed, OSError) as e:
            print(f"disconnected: {e}; reconnect in 3s")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("bye")
            return


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python ws_console_client.py <USER_UUID> [WS_URL]")
        sys.exit(1)

    user_id = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:8001/ws/notifications"

    try:
        asyncio.run(run(user_id, url))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()