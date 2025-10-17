from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
#from routers import user_router, product_router, ai_router, ai_router2
from statistics import emotion

import uvicorn


app = FastAPI()

app.mount("/ui", StaticFiles(directory="ui"), name="ui")

@app.get("/ui", response_class=RedirectResponse)
async def forward_root():
    return "/ui/index.html"

@app.get("/comments/emotion")
async def get_comments_emotion():
    result = emotion.statistics()
    return list(result)[0:9:1]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)