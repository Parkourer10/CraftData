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
Based on the following summary about a Minecraft-related topic, generate several diverse and unique important questions that capture various aspects of the main topic. Your output should strictly follow these rules:

1. Each question must be on its own line with no prefixes (no numbers, bullets, or asterisks)
2. Each question must cover a unique aspect of the summary
3. Questions must be clear, concise, and directly related to Minecraft
4. Questions must be complete sentences ending with a question mark
5. No meta-text, formatting, or additional commentary
6. No questions about versions unless explicitly mentioned in the summary
7. No questions about licensing or website liscensing.

Here's the summary:
{summary}

Questions:"""

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
    
    qa_pairs = []
    for question in questions:
        answer = parse_with_ollama([], "answer", {"summary": summary, "question": question})
        qa_pairs.append((question, answer))
    
    return qa_pairs
