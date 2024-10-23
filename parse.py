from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
template = """
You are tasked with extracting specific information from the following text content: {dom_content}
Please follow these instructions carefully:
1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}
2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response.
3. **Empty Response:** If no information matches the description, return an empty string only.
4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text.
5. **No licensings:** Do not include any licensing or attribution information in your response.
6. **No version information:** Do not include any version information in your response unless asked to do so.
Response:
"""
summary_template = """
Summarize the main content of this webpage about Minecraft in one concise paragraph. Focus on the most important information and key points:
{dom_content}
Summary:
"""
questions_template = """
Based on the following summary about a Minecraft-related topic, generate as many diverse and unique important questions that capture various aspects of the main topic or significant information as you can. Ensure that:
1. Each question covers a different aspect of the summary.
2. No two questions are similar or ask about the same information.
3. Questions are clear, concise, and directly related to Minecraft.
4. Questions do not include any numbering or perspective from an AI or user.
5. Questions focus on game mechanics, features, history, or development.
6. All questions end with a question mark.
7. It shouldn't have any licensings or attribution information in your response.
Summary: {summary}
Questions:
"""
answer_template = """
Provide a concise, factual answer to the following question based on the summary about a Minecraft-related topic. The answer should be informative and directly address the question without asking for further clarification or posing new questions.
Summary: {summary}
Question: {question}
Answer:
"""
model = OllamaLLM(model="llama3.2:3b")
def parse_with_ollama(dom_chunks, parse_type, context=None):
    if parse_type == "summary":
        prompt = ChatPromptTemplate.from_template(summary_template)
        inputs = {"dom_content": dom_chunks[0]}
    elif parse_type == "questions":
        prompt = ChatPromptTemplate.from_template(questions_template)
        inputs = {"summary": context}
    elif parse_type == "answer":
        prompt = ChatPromptTemplate.from_template(answer_template)
        inputs = {"summary": context["summary"], "question": context["question"]}
    else:
        prompt = ChatPromptTemplate.from_template(template)
        inputs = {"dom_content": dom_chunks[0], "parse_description": parse_type}
    
    chain = prompt | model
    response = chain.invoke(inputs)
    return response.strip()
def process_content(dom_chunks):
    summary = parse_with_ollama(dom_chunks, "summary")
    questions_raw = parse_with_ollama([], "questions", summary)
    questions = [q.strip() for q in questions_raw.split('\n') if q.strip() and q.strip().endswith('?')]
    
    results = []
    for question in questions:
        answer = parse_with_ollama([], "answer", {"summary": summary, "question": question})
        results.append({"question": question, "answer": answer})
    
    return results
