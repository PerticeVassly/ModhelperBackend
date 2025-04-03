
class ExtractorLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def extract(self, text: str):
        # Placeholder for the actual extraction logic
        return {"extracted_data": text}


class ChatterLLM:
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    def chat(self, prompt: str):
        # Placeholder for the actual chat logic
        return {"response": f"Chat response for prompt: {prompt}"}


def fomat_response(response):
    # Placeholder for formatting the response
    return response