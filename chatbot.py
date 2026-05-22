import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


# ================= GOOGLE SEARCH =================
def google_search(query):

    try:

        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            json={"q": query},
            timeout=10
        )

        data = response.json()

        results = []

        for item in data.get("organic", [])[:5]:

            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            text = f"{title}\n{snippet}\n{link}"

            results.append(text)

        return "\n\n".join(results)

    except Exception as e:

        print("Search Error:", e)

        return ""


# ================= GROQ CLIENT =================
try:
    client = Groq(api_key=GROQ_API_KEY)

except Exception as e:

    print("Groq Init Error:", e)

    client = None


# ================= EXPENSE ANALYSIS =================
def analyze_expenses(details):

    if not details:
        return "No expense data available."

    lines = details.split("\n")

    overspent = []

    total_planned = 0
    total_actual = 0

    for line in lines:

        try:

            category = line.split(":")[0]

            planned = float(
                line.split("Planned ₹")[1]
                .split(",")[0]
            )

            actual = float(
                line.split("Actual ₹")[1]
            )

            total_planned += planned
            total_actual += actual

            if actual > planned:
                overspent.append(category)

        except:
            pass

    summary = f"""
Total Planned Budget: ₹{round(total_planned,2)}
Total Actual Spending: ₹{round(total_actual,2)}
"""

    if overspent:

        summary += (
            "\n⚠ Overspending detected in: "
            + ", ".join(overspent)
        )

    else:

        summary += "\n✅ Spending is mostly within budget."

    return summary


# ================= FINAL ANSWER =================
def final_answer(
    user_input,
    budget=None,
    details=None,
    venue_data="",
    lat=None,
    lng=None
):

    msg = user_input.lower().strip()

    # ================= SIMPLE GREETINGS =================
    if msg in ["hi", "hello", "hey", "hii"]:

        return (
            "Hello 😊 I'm your AI wedding and event planning assistant. "
            "I can help with venues, budgeting, destination weddings, "
            "expense analysis, event ideas, guest planning, catering, "
            "decorations and much more."
        )

    if "how are you" in msg:

        return (
            "I'm doing great 🎉 Ready to help you plan an amazing event."
        )

    # ================= USER DATA ANALYSIS =================
    expense_analysis = analyze_expenses(details)

    # ================= GOOGLE SEARCH =================
    search_data = google_search(user_input)

    # ================= AI FALLBACK =================
    if client is None:

        return """
🤖 AI service is currently unavailable.

Try asking:
• Suggest wedding venues in Goa
• Analyze my expenses
• Best venue for 500 guests
• How to reduce wedding costs
• Ideas for beach wedding
"""

    # ================= MAIN AI PROMPT =================
    prompt = f"""
You are an advanced AI wedding and event planning assistant.

You behave like ChatGPT.

You give intelligent conversational responses.

You help users with:
- venue recommendations
- destination weddings
- budgeting
- event planning
- expense analysis
- guest management
- wedding themes
- catering
- decorations
- luxury weddings
- affordable weddings

================ USER QUESTION ================
{user_input}

================ USER BUDGET ================
{budget}

================ USER EXPENSE DETAILS ================
{details}

================ AVAILABLE VENUES ================
{venue_data}

================ GOOGLE SEARCH RESULTS ================
{search_data}

================ IMPORTANT RULES ================

1. Reply naturally like ChatGPT.

2. If user asks for wedding venues in a location:
   - recommend suitable venues
   - compare luxury vs affordable options
   - suggest resorts/halls/lawns
   - include venue names naturally
   - mention Google Maps links if available

3. Use the AVAILABLE VENUES section
   to recommend actual venues from database.

4. If user asks budgeting questions:
   analyze their spending intelligently.

5. Give conversational and detailed responses.

6. Avoid robotic replies.

7. Use bullet points when useful.

8. Sound professional and smart.

9. Keep responses engaging and human-like.
"""
    try:

        chat = client.chat.completions.create(

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are a smart AI wedding planning assistant."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            model="llama-3.3-70b-versatile",

            temperature=0.8,

            max_tokens=1024
        )

        answer = chat.choices[0].message.content.strip()

        return answer

    except Exception as e:

        print("Chatbot Error:", e)

        return """
🤖 Sorry, I couldn't process that properly right now.

You can ask me things like:
• Suggest wedding venues in Goa
• Analyze my wedding expenses
• Help me plan a destination wedding
• Best banquet halls for 300 guests
• How to reduce event costs
• Wedding decoration ideas
"""