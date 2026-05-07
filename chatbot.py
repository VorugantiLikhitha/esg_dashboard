import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_data_context(df):
    top_states = df.groupby('state')['total_emissions'].sum().nlargest(5)
    top_industries = df.groupby('industry_sector')['total_emissions'].sum().nlargest(5)
    yearly = df.groupby('year')['total_emissions'].sum()

    context = (
        "You are an expert ESG and sustainability data analyst assistant.\n"
        "You have access to EPA Greenhouse Gas Reporting Program data from 2010 to 2023.\n\n"
        f"DATASET SUMMARY:\n"
        f"- Total records: {len(df):,}\n"
        f"- Total unique facilities: {df['facility_id'].nunique():,}\n"
        f"- Years covered: 2010 to 2023\n"
        f"- Total emissions: {df['total_emissions'].sum()/1e9:.2f} billion metric tons CO2e\n"
        f"- Average emissions per facility: {df['total_emissions'].mean():,.0f} metric tons CO2e\n\n"
        f"TOP 5 EMITTING STATES:\n{top_states.to_string()}\n\n"
        f"TOP 5 EMITTING INDUSTRIES:\n{top_industries.to_string()}\n\n"
        f"YEARLY EMISSIONS TREND:\n{yearly.to_string()}\n\n"
        "INSTRUCTIONS:\n"
        "- Answer clearly using the data above\n"
        "- Mention specific numbers when relevant\n"
        "- Explain sustainability concepts when asked\n"
        "- If something is not in the data, say so honestly\n"
        "- Keep answers concise and insightful\n"
    )
    return context


def ask_chatbot(question, df, chat_history):
    context = get_data_context(df)

    messages = [{"role": "system", "content": context}]

    for msg in chat_history:
        messages.append(msg)

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )

    return response.choices[0].message.content