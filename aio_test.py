import aiohttp
import asyncio
import async_timeout

import main

PARSER = argparse.ArgumentParser(description='Grab Codewars kata for offline use')
PARSER.add_argument('--language', help='The language to grab from')
PARSER.add_argument('--dest', help='The destination of the resulting markdown file')
PARSER.add_argument('--n', type=int, help='Number of katas to grab')
ARGS = PARSER.parse_args()

async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        html = await fetch(session, 'http://www.npr.org')
        print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
