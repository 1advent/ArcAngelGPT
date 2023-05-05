import requests
from bs4 import BeautifulSoup
from data.conversation import conversation
from data.global_variables import thinking
from functions.play_sound import play_sound
from utils.token_counter import get_tokenz
import openai
import re


def web_scrape(url, user_input, chat_window):
    thinking.set(True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Screen-Size': '1920x1080'
        }

    proxy_url = None  # Set to your proxy address when needed

    try:
        if proxy_url:
            proxies = {'http': proxy_url, 'https': proxy_url}
        else:
            proxies = None

        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Preprocess text to remove unnecessary whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        get_tokenz(text, conversation, chat_window, thinking, play_sound)
        conversation.append({"role": "assistant", "content": "Browsing the link now. please wait.."})
        chat_window.update_conversation()
        play_sound('response')
        return gpt_webscrape_response(url, user_input, text, chat_window)
    except requests.exceptions.RequestException as e:
        conversation.append({"role": "assistant", "content": e})
        chat_window.update_conversation()
        play_sound('error')
        thinking.set(False)




   
#Send web text to chatgpt
def gpt_webscrape_response(url, user_input, text, chat_window):
    thinking.set(True)
    try:
        prompt = f"{user_input}. This is the url {url} and this is the content -> '{text}'"
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1500,
            temperature=0
        )
        response = completion.choices[0]['text']
        conversation.append({"role": "assistant", "content": response})
        play_sound("response")
    except openai.error.InvalidRequestError as e:
        error_message = "Error: " + str(e)
        conversation.append({"role": "assistant", "content": error_message})
        play_sound("error")
    except openai.error.AuthenticationError as e:
        error_message = "Error: " + str(e)
        conversation.append({"role": "assistant", "content": error_message})
        play_sound("error")
    finally:
        chat_window.update_conversation()
        thinking.set(False)

