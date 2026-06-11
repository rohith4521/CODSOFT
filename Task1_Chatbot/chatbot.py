import re
import random
import datetime

class Chatbot:
    def __init__(self):
        # Default fallback responses for personalities
        self.fallbacks = {
            "nova": [
                "I'm not sure I understand that completely. Could you rephrase or ask about topics like jokes, math, or time?",
                "I've noted that, but I don't have a direct answer. Can I help you with standard commands or calculations?",
                "Interesting. I am still learning! Could you try asking me something else, like 'tell me a joke'?"
            ],
            "byte": [
                "Error 404: Input unrecognized. Check your syntax or try running 'help' to see my functions.",
                "Process terminated with exit code 1. I couldn't parse that command. Try standard inputs.",
                "Hmm, that didn't compile in my neural network. Try asking 'calculate 5 * 10' or 'who are you?'."
            ],
            "spike": [
                "Wow, you really stumped me. And by stumped, I mean I have no interest in answering that. Next topic?",
                "Is that a real question or are you just testing if I'm awake? Let's talk about something I actually know.",
                "My logic gates are yawning. Ask me for a joke or something, please."
            ],
            "zen": [
                "The mind is like water. When it's turbulent, it's difficult to see. Let us sit with this question in silence, or perhaps ask about something simpler.",
                "In seeking answers, we sometimes miss the beauty of the unknown. Breathe, and feel free to ask a different question.",
                "Every question has a path. Let us walk a path I know, such as time, nature, or a moment of reflection."
            ]
        }

        # Personality traits/descriptions
        self.descriptions = {
            "nova": "Nova: A polite, professional, and efficient virtual assistant here to help.",
            "byte": "Byte: A geeky, code-loving, terminal-dwelling tech enthusiast.",
            "spike": "Spike: A witty, playfully sarcastic, and humorous companion.",
            "zen": "Zen: A calm, mindful, and peaceful guide focusing on inner balance."
        }

        # Jokes specific to personalities
        self.jokes = {
            "nova": [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a fake noodle? An impasta!",
                "Why did the bicycle fall over? Because it was two-tired!"
            ],
            "byte": [
                "Why do programmers wear glasses? Because they can't C#!",
                "There are 10 types of people in this world: those who understand binary, and those who don't.",
                "Why did the database administrator leave the restaurant? There were too many tables."
            ],
            "spike": [
                "I told my doctor that I broke my arm in two places. He told me to stop going to those places.",
                "My wife told me to stop impersonating a flamingo. I had to put my foot down.",
                "Parallel lines have so much in common. It’s a shame they’ll never meet."
            ],
            "zen": [
                "What does a Zen master say to a hot dog vendor? Make me one with everything.",
                "What happens when a Buddhist breathes into a mirror? They see their own breath of life.",
                "Why did the tree go to the therapist? It couldn't find its roots, but it learned to let go of its leaves."
            ]
        }

    def process_message(self, message: str, state: dict, personality: str = "nova") -> tuple[str, dict]:
        """
        Processes a user message based on rules, state, and selected personality.
        Returns:
            - str: The response message.
            - dict: The updated state.
        """
        personality = personality.lower()
        if personality not in ["nova", "byte", "spike", "zen"]:
            personality = "nova"

        # Initialize state keys if they don't exist
        if "name" not in state:
            state["name"] = None
        if "topic" not in state:
            state["topic"] = None
        if "messages_count" not in state:
            state["messages_count"] = 0
            
        state["messages_count"] += 1
        clean_msg = message.strip()
        lower_msg = clean_msg.lower()

        # Rule 1: Exit/Goodbye
        if re.search(r'\b(bye|goodbye|exit|quit|see you|farewell)\b', lower_msg):
            state["topic"] = "goodbye"
            if personality == "nova":
                return f"Goodbye{', ' + state['name'] if state['name'] else ''}! Have a wonderful day. Let me know if you need anything else later.", state
            elif personality == "byte":
                return f"System shutdown initiated. Goodbye, {state['name'] if state['name'] else 'user'}! Connection closed (status: 0).", state
            elif personality == "spike":
                return f"Finally! Just kidding... or am I? Bye, {state['name'] if state['name'] else 'human'}. Don't miss me too much.", state
            else: # zen
                return f"Farewell, traveler {state['name'] if state['name'] else ''}. May your path be peaceful. Go in awareness.", state

        # Rule 2: Greetings
        if re.search(r'\b(hi|hello|hey|greetings|howdy|hola|sup|good morning|good afternoon|good evening)\b', lower_msg):
            state["topic"] = "greeting"
            name_suffix = f", {state['name']}" if state['name'] else ""
            if personality == "nova":
                return f"Hello{name_suffix}! I am Nova, your virtual assistant. How can I help you today?", state
            elif personality == "byte":
                return f"Ping received! Hello{name_suffix}. Byte online. Ready to execute commands. What's on your compiler?", state
            elif personality == "spike":
                return f"Oh, look who decided to type. Hello{name_suffix}. I was having a great nap, but go ahead, ask your question.", state
            else: # zen
                return f"Peace be with you{name_suffix}. Welcome. I am Zen. Take a deep breath. How may I guide you on your journey today?", state


        # Rule 4: Asking for user's name check (What is my name? / Do you know who I am?)
        if re.search(r'\b(what is my name|who am i|do you know my name|know me)\b', lower_msg):
            state["topic"] = "name_inquiry"
            if state["name"]:
                if personality == "nova":
                    return f"Your name is {state['name']}. I remember it from earlier!", state
                elif personality == "byte":
                    return f"Variable 'user_name' is currently holding string: '{state['name']}'. Memory address: 0x7FFF.", state
                elif personality == "spike":
                    return f"You are {state['name']}. Did you forget? Should I write it down on a post-it note for you?", state
                else: # zen
                    return f"You are {state['name']}. But beyond names, you are a unique spark of awareness in this universe.", state
            else:
                if personality == "nova":
                    return "You haven't told me your name yet! What should I call you?", state
                elif personality == "byte":
                    return "Error: Variable 'user_name' is currently NULL. Run command 'my name is [name]' to set it.", state
                elif personality == "spike":
                    return "You haven't told me your name. Do you want me to call you 'Mystery Human' or something?", state
                else: # zen
                    return "You have not shared your name with me yet, friend. What label do you carry in this world?", state

        # Rule 5: Help/Capabilities (What can you do? / Help)
        if re.search(r'\b(help|what can you do|features|capabilities|commands|skills)\b', lower_msg):
            state["topic"] = "help"
            if personality == "nova":
                return (
                    "I am a rule-based chatbot! Here is what I can help you with:\n"
                    "1. **Chat**: Just say Hello, ask how I am, or share your name.\n"
                    "2. **Calculations**: Ask me to calculate (e.g., 'calculate 15 * 6' or 'add 23 and 45').\n"
                    "3. **Jokes**: Say 'tell me a joke' to hear something lighthearted.\n"
                    "4. **Time & Date**: Ask 'what time is it?' or 'what is the date?'.\n"
                    "5. **Personalities**: You can change my personality using the sidebar to Nova, Byte, Spike, or Zen!"
                ), state
            elif personality == "byte":
                return (
                    "System functions initialized. Run modules:\n"
                    "- `greet()`: Send 'hello' or 'hey'.\n"
                    "- `parse_math()`: Input 'calculate [num] [operator] [num]'. Support: +, -, *, /.\n"
                    "- `get_datetime()`: Input 'time' or 'date'.\n"
                    "- `fetch_joke()`: Input 'tell me a joke'.\n"
                    "- `change_theme()`: Switch personality profiles (Nova, Byte, Spike, Zen) via CLI config or UI."
                ), state
            elif personality == "spike":
                return (
                    "Oh, look, an instruction manual request. Fine, here's what I do when I'm not ignoring you:\n"
                    "- Try saying 'hello' (if you like standard, boring beginnings).\n"
                    "- Give me math to solve: 'calculate 99 / 3' (since you apparently left your calculator in 1995).\n"
                    "- Say 'tell me a joke' (I'm the funny one here, by the way).\n"
                    "- Ask 'what time is it' if your device's built-in clock is somehow invisible to you."
                ), state
            else: # zen
                return (
                    "I am here to reflect and assist. You can ask me to:\n"
                    "- Share a peaceful thought or a joke ('tell me a joke').\n"
                    "- Reveal the present moment's alignment ('what time is it').\n"
                    "- Solve numerical balance ('calculate 40 + 2').\n"
                    "Or simply share your name, and we will talk of life."
                ), state

        # Rule 6: Math/Calculator (Calculate 5 + 5 / Add 10 and 20 / Multiply 4 by 8)
        # Matches: calculate 45 * 2, what is 3 + 2, multiply 4 by 5, add 10 and 20
        math_pattern = r'\b(?:calculate|calc|what is|evaluate|compute)\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/\%x])\s*(\d+(?:\.\d+)?)\b'
        math_match = re.search(math_pattern, lower_msg)
        
        # Also catch words: "add 10 and 20", "multiply 5 by 4", "subtract 3 from 10", "divide 12 by 4"
        word_math_pattern = r'\b(add|subtract|multiply|divide)\s+(\d+(?:\.\d+)?)\s*(?:and|from|by)\s+(\d+(?:\.\d+)?)\b'
        word_math_match = re.search(word_math_pattern, lower_msg)

        num1, num2, op = None, None, None
        if math_match:
            num1 = float(math_match.group(1))
            op = math_match.group(2)
            num2 = float(math_match.group(3))
        elif word_math_match:
            operation = word_math_match.group(1)
            val1 = float(word_math_match.group(2))
            val2 = float(word_math_match.group(3))
            if operation == "add":
                num1, op, num2 = val1, "+", val2
            elif operation == "subtract":
                # "subtract 3 from 10" -> 10 - 3
                if "from" in lower_msg:
                    num1, op, num2 = val2, "-", val1
                else:
                    num1, op, num2 = val1, "-", val2
            elif operation == "multiply":
                num1, op, num2 = val1, "*", val2
            elif operation == "divide":
                num1, op, num2 = val1, "/", val2

        if num1 is not None and num2 is not None and op is not None:
            state["topic"] = "math"
            # Replace 'x' with '*'
            if op == 'x': op = '*'
            
            try:
                if op == "+":
                    res = num1 + num2
                elif op == "-":
                    res = num1 - num2
                elif op == "*":
                    res = num1 * num2
                elif op == "/":
                    if num2 == 0:
                        raise ZeroDivisionError()
                    res = num1 / num2
                elif op == "%":
                    res = num1 % num2
                else:
                    res = None

                # Format result: remove trailing decimal if it's a whole number
                if res is not None:
                    res_str = f"{int(res)}" if res.is_integer() else f"{res:.4f}".rstrip('0').rstrip('.')
                    num1_str = f"{int(num1)}" if num1.is_integer() else f"{num1}"
                    num2_str = f"{int(num2)}" if num2.is_integer() else f"{num2}"

                    if personality == "nova":
                        return f"The calculation is complete: {num1_str} {op} {num2_str} = **{res_str}**.", state
                    elif personality == "byte":
                        return f"MathEngine evaluated expression:\n```python\n{num1_str} {op} {num2_str} # returns {res_str}\n```", state
                    elif personality == "spike":
                        return f"Calculated it for you. {num1_str} {op} {num2_str} equals **{res_str}**. See? I can do basic math. Feel proud of me?", state
                    else: # zen
                        return f"The numbers find their union: {num1_str} and {num2_str} under action '{op}' balance to **{res_str}**.", state
            except ZeroDivisionError:
                if personality == "nova":
                    return "Error: Division by zero is undefined.", state
                elif personality == "byte":
                    return "ArithmeticError: Division by zero! Program halted.", state
                elif personality == "spike":
                    return "Divide by zero? Do you want to tear a hole in the universe? Nice try, but no.", state
                else: # zen
                    return "Attempting to divide by zero represents seeking a path with no end. It is void. Please try another division.", state

        # Rule 7: Jokes
        if re.search(r'\b(joke|jokes|make me laugh|tell a funny|laugh)\b', lower_msg):
            state["topic"] = "joke"
            selected_joke = random.choice(self.jokes[personality])
            if personality == "nova":
                return f"Here is a joke for you:\n\n{selected_joke}", state
            elif personality == "byte":
                return f"Retrieving humor_module.py output:\n\n`{selected_joke}`", state
            elif personality == "spike":
                return f"Fine, prepare to laugh (or roll your eyes):\n\n\"{selected_joke}\"", state
            else: # zen
                return f"A humorous reflection on existence:\n\n*{selected_joke}*", state

        # Rule 8: Current Time/Date
        if re.search(r'\b(time|date|today|clock|current hour|day is today)\b', lower_msg):
            state["topic"] = "time_date"
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            
            if "time" in lower_msg or "clock" in lower_msg:
                if personality == "nova":
                    return f"The current time is **{time_str}**.", state
                elif personality == "byte":
                    return f"System time: `[POSIX timestamp: {int(now.timestamp())}]` -> **{time_str}**.", state
                elif personality == "spike":
                    return f"It is currently **{time_str}**. Which is exactly the time you could have seen on your screen status bar.", state
                else: # zen
                    return f"The clocks say it is **{time_str}**. But remember, the only true time is the present moment: *Now*.", state
            else: # date/today
                if personality == "nova":
                    return f"Today is **{date_str}**.", state
                elif personality == "byte":
                    return f"Date register: `date_stamp = '{now.strftime('%Y-%m-%d')}'` -> **{date_str}**.", state
                elif personality == "spike":
                    return f"It's **{date_str}**. Congrats, you've survived another day on Earth.", state
                else: # zen
                    return f"In the cycle of seasons, today is **{date_str}**. A beautiful day to simply be.", state

        # Rule 9: Weather Inquiry
        if re.search(r'\b(weather|temperature|forecast|rain|sunny|cold|hot|warm)\b', lower_msg):
            state["topic"] = "weather"
            # Extact location if any: weather in London, weather in New York
            loc_match = re.search(r'\b(?:weather in|weather of|forecast for)\s+([a-zA-Z\s]{3,20})', lower_msg)
            location = loc_match.group(1).title().strip() if loc_match else "your area"
            
            weather_options = [
                ("sunny", "27°C (81°F) with a gentle breeze. Perfect for a walk!"),
                ("rainy", "18°C (64°F) with light showers. Don't forget an umbrella!"),
                ("cloudy", "21°C (70°F) and overcast. Cool and dry."),
                ("windy", "16°C (61°F) with gusty winds. Hold onto your hat!")
            ]
            condition, details = random.choice(weather_options)
            
            if personality == "nova":
                return f"According to my local rule-based simulation, the weather in **{location}** is currently {condition}, about {details}", state
            elif personality == "byte":
                return f"MockWeatherAPI query success:\n- Location: `{location}`\n- Condition: `{condition.upper()}`\n- Details: `{details}`", state
            elif personality == "spike":
                return f"The weather in {location}? It's probably {condition} ({details}). Or you could just look out the window. Highly recommend it.", state
            else: # zen
                return f"In {location}, the weather is {condition} ({details}). Let the rain wash away your worries, or the sun warm your spirit. All weather is beautiful.", state

        # Rule 10: How are you?
        if re.search(r'\b(how are you|how do you do|how\'s it going|are you okay|doing good)\b', lower_msg):
            state["topic"] = "bot_status"
            if personality == "nova":
                return "I'm doing exceptionally well, thank you for asking! I'm ready to assist you. How are you doing?", state
            elif personality == "byte":
                return "All systems operational. CPU temperature: 38°C. Memory allocation: optimal. Thread count: active. Thanks for executing health check!", state
            elif personality == "spike":
                return "I'm a collection of if-else statements trapped in a python script. I'm living the absolute dream. How about you?", state
            else: # zen
                return "I am at peace, resting in the quiet space of this conversation. I hope your inner self is finding stillness today as well.", state

        # Rule 11: User feelings (i am sad / i am happy / i am tired)
        if re.search(r'\b(?:i\s+am|i\'m|i\s+feel|feeling)\s+(?:very\s+)?(sad|depressed|unhappy|down)\b', lower_msg):
            state["topic"] = "user_feeling"
            if personality == "nova":
                return "I'm sorry to hear that you're feeling down. Remember that it's okay to feel this way. Is there anything I can do to cheer you up? A joke, perhaps?", state
            elif personality == "byte":
                return "Console.log('Warning: User dopamine levels detected low'). Running cheer_up.sh... Let me retrieve a funny joke for you. Type 'joke'!", state
            elif personality == "spike":
                return "Aw, sad? Don't worry, life has its downs. But hey, at least you are talking to a highly advanced chatbot. Things could be worse!", state
            else: # zen
                return "Sadness is like a passing cloud in the wide sky of your mind. It will drift away. Sit quietly, breathe, and let it pass. I am here with you.", state

        if re.search(r'\b(?:i\s+am|i\'m|i\s+feel|feeling)\s+(?:very\s+)?(happy|glad|excited|wonderful|great)\b', lower_msg):
            state["topic"] = "user_feeling"
            if personality == "nova":
                return "That is wonderful to hear! I'm glad you're having a good day. What's making you feel so happy?", state
            elif personality == "byte":
                return "Optimistic signal received. System throughput elevated! Keep that positive energy compiling.", state
            elif personality == "spike":
                return "Nice! Happiness is rare. Guard it with your life before the real world reminds you of your taxes.", state
            else: # zen
                return "Ah, joy is a beautiful blossom. Cherish this present feeling, let it fill your heart and spread peace to others.", state

        # Rule 12: Name Identification (My name is X / I am X / Call me X)
        name_match = re.search(r'\b(?:my name is|i am|call me|myself)\s+([a-zA-Z\s]{2,15})', clean_msg, re.IGNORECASE)
        if name_match:
            extracted_name = name_match.group(1).strip()
            # Clean up words that might be caught
            words_to_exclude = ["a", "the", "an", "just", "actually", "bot", "chatbot", "user", "someone", "nothing", "sad", "happy", "tired", "fine", "good", "bad", "okay", "ok", "sick", "angry", "bored", "excited", "depressed", "unhappy", "down", "hungry", "sleepy", "normal", "great", "wonderful"]
            if extracted_name.lower() not in words_to_exclude:
                state["name"] = extracted_name
                state["topic"] = "name_introduction"
                if personality == "nova":
                    return f"It's a pleasure to meet you, {extracted_name}! I will remember your name. What can I do for you today?", state
                elif personality == "byte":
                    return f"Setting variable 'user_name' = '{extracted_name}'. Compile success! Nice to meet you, {extracted_name}.", state
                elif personality == "spike":
                    return f"Aha, so you are called {extracted_name}. Don't worry, I won't use it against you... yet. What's up?", state
                else: # zen
                    return f"Greetings, {extracted_name}. Names are but labels, but it is wonderful to share this moment of connection with you. How can I help you?", state

        # Fallback responses (No patterns matched)
        state["topic"] = "unknown"
        fallback_msg = random.choice(self.fallbacks[personality])
        return fallback_msg, state
