import os
from openai import AzureOpenAI
import base64
import json
import time
import errno

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-12-01-preview"
)


def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)



def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    response = client.chat.completions.create(
        # model="gpt-4-vision-preview",
        model= "gpt-4v",
        messages=[
            {
                "role": "system",
                "content": """
                Pretend these photos are a storyboard. Analysis the picture of the human or humans. Focus on facial features, clothing, and hand gestures.
                State what is happening in each photo. Don't repeat yourself. Keep it short and concise. Guess what the context of the photo is. Connect the pictures into a story. If there is anything remotely interesting, make a big deal about it! Do not use the words image or photograph.
                """,
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def story_gen():
    script = []
    i=1

    while True and i < 7:
        # path to your image
        # image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")
        image_path = os.path.join(os.getcwd(), f"static/images/story{i}.png")
        i+=1

        # getting the base64 encoding
        b64_image = encode_image(image_path)

        # analyze posture
        print("Generating Story...")
        analysis = analyze_image(b64_image, script=script)

        print("You're Story is:")
        print(analysis)
        

        script = script + [{"role": "assistant", "content": analysis}]

    return script

        # # wait for 5 seconds
        # time.sleep(5)




if __name__ == "__main__":
     story_gen()
