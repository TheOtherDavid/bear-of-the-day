import os
from openai import OpenAI

def generate_image(prompt):
  try:
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    print('Generating image...')
    response = client.images.generate(
      model="dall-e-3", 
      prompt=prompt,
      size="1024x1024",
      quality="standard",
      n=1
    )
    print('Image generated!')

    image_url = response.data[0].url

    return image_url
  except OpenAI.APIError as e:
    print(f"An error occurred while generating the image: {e}")
    return None
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return None