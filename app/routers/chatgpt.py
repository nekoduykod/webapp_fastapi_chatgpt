import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openai

load_dotenv("../../.env")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "not-set-api-key")


class OpenAIDependency:
   def __init__(self, api_key: str = Depends(get_openai_api_key)):
      self.client = openai.OpenAI(api_key=api_key)


client = OpenAIDependency().client


@router.get('/chatgpt', response_class=HTMLResponse)
async def gpt_page(request: Request, user_message: str = "", generated_message: str = ""):
   return templates.TemplateResponse("gpt.html", {"request": request, "user_message": user_message, "generated_message": generated_message})


@router.post('/chatgpt', response_class=HTMLResponse)
async def chat_with_gpt(request: Request, message: str = Form(...), openai_dependency: OpenAIDependency = Depends()):
   if not message:
      return templates.TemplateResponse("gpt.html", {"request": request, "error": "Message cannot be empty"})

   try:
      response = openai.Completion.create(
         engine="gpt-3.5-turbo",
         prompt=message,
         max_tokens=100,
        )
      generated_message = response.choices[0].text.strip()
      
   except Exception as e:
      return templates.TemplateResponse("gpt.html", {"request": request, "error": f"Error generating response: {str(e)}"})
    
   return templates.TemplateResponse("gpt.html", {"request": request, "user_message": message, "generated_message": generated_message})
