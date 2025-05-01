import os
from openai import OpenAI, APIError

def generate_image(prompt):
  try:
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    print('Generating image...')
    response = client.images.generate(
      model="gpt-image-1", 
      prompt=prompt,
      size="1024x1024",
      quality="medium",
      n=1
    )
    print('Image generated!')

    image_url = response.data[0].url

    return image_url
  except APIError as e:
    print(f"An error occurred while generating the image: {e}")
    return None
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return None