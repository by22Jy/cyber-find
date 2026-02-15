from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .core import CyberFind, OutputFormat, SearchMode

app = FastAPI(title="CyberFind API", version="0.3.3")

cyberfind = CyberFind()


class SearchRequest(BaseModel):
    usernames: List[str]
    sites_file: Optional[str] = None
    mode: str = "standard"
    output_format: str = "json"
    max_concurrent: int = 50


@app.get("/")
async def root():
    return {"message": "CyberFind API", "version": "0.3.3"}


@app.post("/search")
async def search(request: SearchRequest):
    try:
        mode = SearchMode(request.mode)
        output_format = OutputFormat(request.output_format)

        results = await cyberfind.search_async(
            usernames=request.usernames,
            sites_file=request.sites_file,
            mode=mode,
            output_format=output_format,
            max_concurrent=request.max_concurrent,
        )

        return {"success": True, "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    try:
        import sqlite3

        conn = sqlite3.connect("cyberfind.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM statistics ORDER BY date DESC LIMIT 10")
        stats = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM search_results")
        total_searches = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM search_results WHERE found = 1")
        total_found = cursor.fetchone()[0]

        conn.close()

        return {
            "recent_stats": stats,
            "total_searches": total_searches,
            "total_found": total_found,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_api_server(host: str = "0.0.0.0", port: int = 8080):
    import uvicorn

    uvicorn.run(app, host=host, port=port)
