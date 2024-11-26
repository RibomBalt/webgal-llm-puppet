import argparse
import httpx
from pydantic import BaseModel
import asyncio


class NewChatResp(BaseModel):
    sess_id: str
    system_prompt: str
    welcome: str


def parse_arg():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        "-u",
        type=str,
        default="http://127.0.0.1:10228/api",
        help="URL of the server",
    )

    parser.add_argument(
        "--bot",
        "-b",
        type=str,
        default="pure",
        help="preset of prompts",
    )

    parser.add_argument(
        "--system-prompts",
        "-s",
        type=str,
        default="",
        help="overwrite system prompts in preset",
    )

    parser.add_argument(
        "--welcome",
        "-w",
        type=str,
        default="",
        help="overwrite welcome message in preset",
    )

    return parser.parse_args()


async def main(args):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{args.url}/newchat",
            params={
                "bot": args.bot,
                "system": args.system_prompts,
                "welcome": args.welcome,
            },
        )
        sess = NewChatResp.model_validate(resp.json())
        print(sess)
        print('\n======')

        while True:
            prompt = input("User: ")
            if prompt == "EOF":
                return
            print('\n======')

            if prompt == 'exit':
                print('Bye')
                break

            async with client.stream(
                "POST",
                f"{args.url}/chat/{sess.sess_id}", data={"msg": prompt}, 
            ) as resp:
                print("Bot: \n")
                async for chunk in resp.aiter_text():
                    print(chunk, end='')

            print('\n======')



if __name__ == "__main__":
    """
    """
    args = parse_arg()
    asyncio.run(main(args))
