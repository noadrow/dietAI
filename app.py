from flask import Flask, request, render_template_string
from google import genai
import os

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="get your own one bitch")

app = Flask(__name__)

data_today = {'שומנים': 0.0, 'חלבונים': 0.0, 'פחמימות': 0.0}
css_template = """
body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 20px;
      background: #f8f9fa;
      color: #333;
    }
    h2 {
      color: #2c3e50;
    }
    .nutrition {
      background: #fff;
      padding: 15px;
      border-radius: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .nutrition strong {
      color: #27ae60;
    }
    .nutrients {
      display: flex;
      gap: 20px;
      margin-top: 10px;
    }
    .nutrients div {
      background: #ecf0f1;
      padding: 10px;
      border-radius: 8px;
      min-width: 100px;
      text-align: center;
    }
    .advice {
      background: #e8f5e9;
      border-right: 5px solid #2ecc71;
      padding: 15px;
      border-radius: 8px;
    }
    ul {
      margin-top: 10px;
    }"""

def add_nutrients(total, new_entry):
    for key in total:
        if key in new_entry:
            total[key] += new_entry[key]
    return total

def process(text):
    import re
    numbers = {}

    # Regex to extract the part inside <>
    if len(text.split(":")) > 1:
        name, value, _ = text.split(":", 2)
        if (any(v.isdigit() for v in value)):
            numbers[name.strip()] = float(re.search(r"[\d.]+", value).group())
        else:
            pass
    html_template_AI_answer = re.findall(r"<([^<>]+)>", text)

    return [numbers,html_template_AI_answer]


@app.route("/hello", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        amount = request.form.get("amount")
        food_type = request.form.get("food_type")
        calories = request.form.get("calories")

        content = f"""
        תאריך את  הקלוריות פחממות  שומנים וחלבונים לפי המידע הבא:
        {amount},{food_type},{calories}
        תענה בדפוס הבא: 
        <שומנים:תשובה><חלבונים:תשובה><פחמימות:תשובה>
        ותן עצה תזונאית לחולי סכרת
        נסח הכל בתצוגה גרפית של HTML 
        קח בחשבון שאתה שולח string לתוך פייתון
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=content
        )

        # Get the text from the input named 'userInput'
        user_text = request.form.get("userInput")
        # Do something with user_text here
        print(content)
        print(response)

        data,html_template_AI_answer = process(str(response.text))
        add_nutrients(data_today, data)

        return (f"{str(response.text)}")


    # For GET, just show the form
    html_block = f"""
    <!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>מעקב תזונה</title>
  <style>
    {css_template}
  </style>
    <body>
        <h1>Diet App</h1>
        <div class="nutrition">
        <p><strong>סיכום יומי:</strong></p>
        <p>{data_today}</p>
        </div>
        <form action="/hello" method="post">
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Amount</th>
                        <th>Food Type</th>
                        <th>Calories</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><input type="text" name="amount" required /></td>
                        <td><input type="text" name="food_type" required /></td>
                        <td><input type="text" name="calories" required /></td>
                    </tr>
                </tbody>
            </table>
            <br />
            <button type="submit">Send</button>
        </form>
    </body>
</body>
    </html>
    """

    return html_block


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
