import os
import json  
#for encoding and decoding data
from bs4 import BeautifulSoup

def parse_document(file_path):
    #opening one json webpagefile
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    #getting webpage url and html content from json
    url = data["url"]
    content = data["content"]
    soup = BeautifulSoup(content, "html.parser")

    text = soup.get_text(separator=" ", strip = True)

    important_text_content = []

    tags = ["title", "h1", "h2", "h3", "b", "strong"]
    for tag in soup.find_all(tags):
        important_text_content.append(tag.get_text(separator=" ", strip=True))

    return {
        "url": url,
        "text": text,
        "important_text": " ".join(important_text_content)
    }

if __name__ == "__main__":
    DEV_FOLDER = "DEV"

    for root, dirs, files in os.walk(DEV_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)

            result = parse_document(file_path)

            print("URL:")
            print(result["url"])

            print("\nCLEAN TEXT SAMPLE:")
            print(result["text"][:500])

            print("\nIMPORTANT TEXT SAMPLE:")
            print(result["important_text"][:500])

            exit()