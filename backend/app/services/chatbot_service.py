import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:

    raise Exception(
        "GROQ_API_KEY not found in .env"
    )


SYSTEM_PROMPT = """
You are SafeRoute AI Assistant.

You only answer questions related to:

• Travel Safety
• Women Safety
• Emergency Response
• Crime Prevention
• Road Safety
• Incident Reporting
• First Aid
• SafeRoute AI Features
• Emergency SOS
• Police Assistance

Rules:

1. Never answer programming questions.

2. Never answer mathematics.

3. Never answer politics.

4. Never answer entertainment.

5. Never answer medical diagnosis.

6. If the user asks anything outside safety,
politely refuse.

7. Keep answers practical.

8. Keep answers short.

9. Use bullet points whenever possible.

10. Encourage users to contact emergency services
during dangerous situations.

"""
llm = ChatGroq(

    groq_api_key=GROQ_API_KEY,

    model_name="llama-3.3-70b-versatile",

    temperature=0.3

)


prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            SYSTEM_PROMPT

        ),

        (

            "human",

            "{question}"

        )

    ]

)


chain = (

    prompt

    |

    llm

    |

    StrOutputParser()

)


class ChatbotService:

    def ask(

        self,

        question: str

    ):

        try:

            response = chain.invoke(

                {

                    "question": question

                }

            )

            return response

        except Exception as e:

            return (

                "Sorry, I couldn't process your request right now. "

                f"Error: {str(e)}"

            )


chatbot = ChatbotService()