import google.generativeai as genai

API_KEY = "AQ.Ab8RN6IZmp6k6MweCBxydbgupWc_hC272CZhnyeiQiy6b_oeTA"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Hello")

print(response.text)