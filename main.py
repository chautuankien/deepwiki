from deepwiki.tools.repo_fetcher import fetch

async def main():
    repo_url = "https://github.com/chautuankien/PhilosoAgent"
    repo_type = "github"
    try:
        repo_data = await fetch(repo_url=repo_url, repo_type=repo_type)
        print(f"Repository fetched successfully: {repo_data.name}")
    except Exception as e:
        print(f"Error fetching repository: {e}")
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
