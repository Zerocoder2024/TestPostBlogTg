import os
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests

app = FastAPI()

openai.api_key = os.environ["OPENAI_API_KEY"]

class Topic(BaseModel):
    topic: str

def get_recent_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey=46bc7c4d105847e6a61ee7e56fdee7fa"
    response = requests.get(url)
    articles = response.json()["articles"]
    recent_news = [article["title"] for article in articles[:3]]
    return "\n".join(recent_news)

def generate_post(topic):
    recent_news = get_recent_news(topic)

    prompt_title = f"Придумайте привлекательный заголовок для поста на тему: {topic}"
    response_title = openai.Completion.create(
        model="gpt-4",
        prompt=prompt_title,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    title = response_title.choices[0].text.strip()

    prompt_meta = f"Напишите краткое, но информативное мета-описание для поста с заголовком: {title}"
    response_meta = openai.Completion.create(
        model="gpt-4",
        prompt=prompt_meta,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    meta_description = response_meta.choices[0].text.strip()

    prompt_post = f"Напишите подробный и увлекательный пост для блога на тему: {topic}, учитывая следующие последние новости:\n{recent_news}\n\nИспользуйте короткие абзацы, подзаголовки, примеры и ключевые слова для лучшего восприятия и SEO-оптимизации."
    response_post = openai.Completion.create(
        model="gpt-4",
        prompt=prompt_post,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    post_content = response_post.choices[0].text.strip()

    return {
        "title": title,
        "meta_description": meta_description,
        "post_content": post_content
    }

@app.post("/generate-post")
async def generate_post_api(topic: Topic):
    generated_post = generate_post(topic.topic)
    return generated_post

@app.get("/heartbeat")
async def heartbeat_api():
    return {"status": "OK"}
