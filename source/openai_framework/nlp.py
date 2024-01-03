from openai import OpenAI

class NLP:

    def conferenceNLP(conference,user_key, temperature=0, model="gpt-3.5-turbo"):
        client = OpenAI(api_key=user_key)
        MODEL = model
        query="Please perform NLP on the following prompt and export the entities with their type as a JSON file: " +conference

        response=client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": query}],
            temperature=temperature
        )
        return(response.choices[0].message.content.strip())
