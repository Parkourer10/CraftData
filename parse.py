import asyncio
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from config import MAX_CONCURRENT_OLLAMA, summary_template, questions_template, answer_template, MODEL
#logging if only we got a error:
logging.getLogger("httpx").setLevel(logging.WARNING)


class ModelPool:
    def __init__(self, size: int = MAX_CONCURRENT_OLLAMA):
        self.models = [
            OllamaLLM(model=MODEL) #model name to use
            for _ in range(size)
        ]
        self.current = 0
        
    def get_next(self):
        model = self.models[self.current]
        self.current = (self.current + 1) % len(self.models)
        return model

class ContentProcessor:
    def __init__(self):
        self.model_pool = ModelPool()
        
        # Create prompt templates
        self.summary_prompt = ChatPromptTemplate.from_template(summary_template)
        self.questions_prompt = ChatPromptTemplate.from_template(questions_template)
        self.answer_prompt = ChatPromptTemplate.from_template(answer_template)

    def parse_with_ollama(self, dom_chunks: List[str], parse_type: str, context: Dict = None) -> str:
        model = self.model_pool.get_next()
        
        if parse_type == "summary":
            chain = self.summary_prompt | model
            inputs = {"dom_content": dom_chunks[0]}
        elif parse_type == "questions":
            chain = self.questions_prompt | model
            inputs = {"summary": context}
        elif parse_type == "answer":
            chain = self.answer_prompt | model
            inputs = {"summary": context["summary"], "question": context["question"]}
            
        response = chain.invoke(inputs)
        return response.strip()

    async def process_content(self, url: str, content: str) -> List[Dict]:
        # Clean content
        soup = BeautifulSoup(content, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()
        cleaned_content = ' '.join(soup.get_text().split())
        
        # Use ThreadPoolExecutor for CPU-bound LLM operations
        with ThreadPoolExecutor() as executor:
            # Get summary
            summary_future = executor.submit(
                self.parse_with_ollama,
                [cleaned_content],
                "summary"
            )
            summary = await asyncio.wrap_future(summary_future)
            
            # Generate questions
            questions_future = executor.submit(
                self.parse_with_ollama,
                [],
                "questions",
                summary
            )
            questions_text = await asyncio.wrap_future(questions_future)
            questions = [q.strip() for q in questions_text.split('\n') 
                        if q.strip() and q.strip().endswith('?')]
            
            # Generate answers in parallel using multiple models
            answer_futures = []
            for question in questions:
                context = {"summary": summary, "question": question}
                answer_futures.append(
                    executor.submit(
                        self.parse_with_ollama,
                        [],
                        "answer",
                        context
                    )
                )
            
            answers = await asyncio.gather(*[
                asyncio.wrap_future(f) for f in answer_futures
            ])
            
            # Create QA pairs
            qa_pairs = []
            for question, answer in zip(questions, answers):
                if answer.strip():  # Only include if we got a non-empty answer
                    qa_pairs.append({
                        "url": url,
                        "question": question,
                        "answer": answer.strip()
                    })
            
            return qa_pairs