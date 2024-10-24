from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
#oh god..
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
Based on the following summary about a Minecraft-related topic, generate a comprehensive set of at least 15-20 or as many as you can and diverse and unique questions. Your questions should thoroughly explore all aspects of the topic, including gameplay mechanics, features, strategies, and interactions. Each question must follow these strict formatting rules:

1. Each question must be on its own line
2. NO prefixes of any kind (no numbers, Q:, bullets, or any other characters before the question)
3. Each question must start directly with a capital letter
4. Each question must be a complete sentence ending with a question mark
5. No blank lines between questions
6. No additional formatting or commentary
7. No questions about versions unless explicitly mentioned in the summary
8. No questions about licensing

Consider these aspects when generating questions:
- Basic mechanics and functionality
- Advanced usage and strategies
- Interactions with other game elements
- Common problems and solutions
- Tips and tricks
- Resource requirements
- Game world interactions
- Player benefits and advantages
- Common misconceptions
- Historical significance in the game

Example format:
How do players craft a wooden pickaxe?
What materials are needed to build a nether portal?
Where can players find diamond ore in the game?
What are the primary benefits of using this item?
How does this feature interact with redstone mechanisms?
What strategies do experienced players use to maximize efficiency?
In what biomes can players commonly find this resource?
What are the potential dangers when utilizing this feature?
How does weather affect this game mechanic?
What alternatives exist for players in early game stages?

Summary: {summary}

Questions:"""

# answer_template = """
# Provide a concise, factual answer to the following question based on the summary about a Minecraft-related topic. The answer must:
# 1. Be a single paragraph
# 2. Start directly with a capital letter (no A:, prefixes, or special characters)
# 3. Be informative and directly address the question
# 4. Not pose new questions or ask for clarification
# 5. Not include any prefixes, numbers, or special formatting

# Summary: {summary}
# Question: {question}

# Answer:"""

answer_template = """
Using ONLY the information provided in the summary, answer the following question about a Minecraft-related topic. Your answer must:

1. ONLY use information explicitly stated in the summary - do not add any external knowledge
2. If the information is not directly mentioned in the summary, respond with "This information is not mentioned in the summary."
3. Be a complete sentence with proper grammar
4. Start with a capital letter and end with proper punctuation
5. Be factual and precise - no speculation or assumptions
6. Not include any prefixes or special formatting

If multiple possible answers exist in the summary, include only the most relevant one. If the information needed for a complete answer is not in the summary, do not try to fill in gaps with assumed information.

Summary: {summary}
Question: {question}

Answer:"""

model = OllamaLLM(model="llama3.2:3b")#added support for qwen2:0.5b :D

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
    

    questions = []
    for line in questions_raw.split('\n'):
        line = line.strip()
        if line and line.endswith('?'):
            cleaned_question = line
            while cleaned_question and cleaned_question[0].isdigit():
                cleaned_question = cleaned_question.lstrip('0123456789.')
            cleaned_question = cleaned_question.lstrip(' .-:*Q')
            if cleaned_question:
                questions.append(cleaned_question[0].upper() + cleaned_question[1:])
    
    qa_pairs = []
    for question in questions:
        answer = parse_with_ollama([], "answer", {"summary": summary, "question": question})
       
        answer = answer.lstrip(' .-:*A')
        if answer:
            answer = answer[0].upper() + answer[1:]
        qa_pairs.append((question, answer))
    
    return qa_pairs
