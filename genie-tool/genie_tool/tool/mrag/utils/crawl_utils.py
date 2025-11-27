from crawl4ai import AsyncWebCrawler

from .logger_utils import logger


async def async_crawl(url: str) -> str:
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)

        return result.markdown
    except Exception as e:
        logger.error(f"Failed to crawl {url}: {e}")
        return ""


def crawl(url: str) -> str:
    import asyncio
    return asyncio.run(async_crawl(url))
