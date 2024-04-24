from flask import Flask, Response, request
import json
from utils.process_requests import RequestHandler, Requests

app = Flask(__name__)
request_handler = RequestHandler()

@app.route("/health-check", methods=['GET'])
def health_check():
    return Response("All Good!",status=200)

@app.route("/submit_question_and_documents", methods=['POST'])
def submit_question_and_documents():
    """
    This endpoint is used to submit a question and documents to the system.
    revieves a json with the following format:
        {
            "question": "What are our product design decisions?",
            "documents": [
                "<https://example.com/call_log_543234.txt>",
                "<https://example.com/call_log_65w331.txt>",
                "<https://example.com/call_log_662x12.txt>"
            ]
        }
    The question and documents are parsed and submitted to a request queue. 
    It returns status code 200 if the question and documents are submitted successfully.
    """
    body = request.get_json()
    ques = body.get("question")
    docs_url = body.get("documents")

    if ques is None or docs_url is None:
        return Response("Bad Request",status=400)
    
    request_handler.add_request_to_request_queue(ques, docs_url)

    return Response("All Good!",status=200)

@app.route("/get_question_and_facts", methods=['GET'])
def get_question_and_facts():
    """
        Method that returns the response from LLM to the question submitted.
        The method reads fromt the response queue and returns the response in format:
            {
                "question": "What are our product design decisions?",
                "facts": [
                    "The team has decided to go with a modular design for the product.",
                    "The team has decided to focus on a desktop-first design",
                    "The team has decided to provide both dark and light theme options for the user interface."
                ],
                "status": "done | processing ",
            }
        "status": "done" if the response is ready, "processing" if the response is not ready yet.        
    """
    if request_handler.get_from_response_queue() is None:
        response = {"question":request_handler.current_question, "facts": None, "status": "processing"}
        return Response(json.dumps(response),status=200)
    
    response = request_handler.get_from_response_queue()
    return Response(json.dumps(response),status=200)




if __name__ == "__main__":
    app.run()
