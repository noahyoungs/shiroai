from brave import AsyncBrave
import asyncio
import json

brave = AsyncBrave()
goggle_url = "https://raw.githubusercontent.com/NyeUsr/NyeUsr-s-Goggles/main/Research%20Boost"

async def search_brave(query: str, num_results: int=5) -> dict:
    data = await brave.search(
        q=query,
        goggles_id=goggle_url,
        count=num_results,
        result_filter="web",
        search_lang="en",
        safesearch="strict",
    )

    filtered_results = []
    # print(f"Results: {data.web.results}")

    for result in data.web.results:
        filtered_result = {
            'title': result.title,
            'url': str(result.url),
            'description': result.description,
            'page_age': result.page_age,
            'netloc': result.meta_url.netloc,
            'path': result.meta_url.path,
            'profile': {
                'name': result.profile.name if result.profile else "",
                'img': str(result.profile.img) if result.profile else "",
            },
        }
        filtered_results.append(filtered_result)

    return filtered_results

async def main():
    search_results = await search_brave(
        query="cobalt mining",
        num_results=5
    )
    print(search_results)

if __name__ == "__main__":
    asyncio.run(main())