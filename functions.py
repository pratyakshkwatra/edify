from openai import OpenAI
from os import environ
import json
import re
from googlesearch import search
import tldextract

client = OpenAI(api_key=environ['OPENAI_API_KEY'])

MODEL="gpt-4o"

def get_main_domain(url):
    extracted = tldextract.extract(url)
    
    main_domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
    return main_domain

def get_top_search_results(query):
    results = []
    
    try:
        for result in search(query, num_results=5):
            results.append(result)
    except:
        pass
    
    return results

def getTopicsFromChapter(chapter: str, subject: str, grade: str, goal: str) -> list[str]:
    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an assistant that helps students extract topics from chapters to get a better understanding of their syllabus."},
        {"role": "user", "content": f"Return a list of 5 most important the topics that come under the chapter: {chapter}, subject: {subject} (Grade: {grade}) (Student is preparing for {goal}). The response should be in JSON format."}
    ]
    )
    return extractListFromResponse(completion.choices[0].message.content)

def getMCQQuestions(topic: str, chapter: str, grade: str, stream: str) -> list:
    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an assistant that helps students with their exams by generating questions for their exams."},
        {"role": "user", "content": f"Give me 3 MULTIPLE CHOICE questions based on the topic of chapter: {chapter}, topic: {topic} ({grade} - {stream}). The response should be in JSON format. Every object should include the question, option1, option2, option3, option4."}
    ]
    )
    return extractListFromResponse(completion.choices[0].message.content)

def check_answer_per_topic(data: list[dict], topic: str, chapter: str, grade: str, stream: str) -> list[int]:
    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an assistant that helps students with their exams by checking their attempt to questions and scoring them."},
        {"role": "user", "content": f"The given list is a dictionary of objects each representing a question of the topic: {topic}, chapter: {chapter} ({grade} - {stream}). Each question object has the question (question_body), the 4 options that were given to the student and studnet's answer. Check the answer given by the user and score them 1 if it is correct and 0 if it is incorrect. The response should be in JSON format. The JSON object should have a key named scores with a list of all the scores in order as integers. DONOT ADD ANYTHING THAT VIOLATES JSON FORMATTING (LIKE COMMENTS). \n\n {data}"}
    ]
    )
    return extractListFromResponse(completion.choices[0].message.content)

def generate_notes(topic: str, grade: str, stream: str) -> list[int]:
    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an assistant that helps students with their exams by creating notes for them for particular topics. These notes that you create are concise, and instead of teaching the student traditionally, use practical concepts and relations to help the student form an image of the concept in their mind."},
        {"role": "user", "content": f"Prepare notes for a student who is weak in the topic: {topic}, School/College grade/Year: {grade}, Stream: {stream} to help him/her get better at the topic. The notes must not have a heading. The notes should have proper line breaks and line gaps."}
    ]
    )
    return completion.choices[0].message.content

def extractListFromResponse(response: str):
    json_array_str = re.search(r'\[.*\]', response, re.DOTALL).group(0)

    data = json.loads(json_array_str)
    
    return data