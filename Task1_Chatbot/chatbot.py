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

        # Define Regex Patterns
        exit_pat = r'\b(bye|goodbye|exit|quit|see you|farewell)\b'
        greet_pat = r'\b(hi|hello|hey|greetings|howdy|hola|sup|good morning|good afternoon|good evening)\b'
        name_inq_pat = r'\b(what is my name|who am i|do you know my name|know me)\b'
        help_pat = r'\b(help|what can you do|features|capabilities|commands|skills)\b'
        math_pat = r'\b(?:calculate|calc|what is|evaluate|compute)\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/\%x])\s*(\d+(?:\.\d+)?)\b'
        word_math_pat = r'\b(add|subtract|multiply|divide)\s+(\d+(?:\.\d+)?)\s*(?:and|from|by)\s+(\d+(?:\.\d+)?)\b'
        joke_pat = r'\b(joke|jokes|make me laugh|tell a funny|laugh)\b'
        time_date_pat = r'\b(time|date|today|clock|current hour|day is today)\b'
        weather_pat = r'\b(weather|temperature|forecast|rain|sunny|cold|hot|warm)\b'
        status_pat = r'\b(how are you|how do you do|how\'s it going|are you okay|doing good)\b'
        feel_sad_pat = r'\b(?:i\s+am|i\'m|i\s+feel|feeling)\s+(?:very\s+)?(sad|depressed|unhappy|down)\b'
        feel_happy_pat = r'\b(?:i\s+am|i\'m|i\s+feel|feeling)\s+(?:very\s+)?(happy|glad|excited|wonderful|great)\b'
        name_intro_pat = r'\b(?:my name is|i am|call me|myself)\s+([a-zA-Z\s]{2,15})'

        # Evaluate Matches
        exit_matched = bool(re.search(exit_pat, lower_msg))
        greet_matched = bool(re.search(greet_pat, lower_msg))
        name_inq_matched = bool(re.search(name_inq_pat, lower_msg))
        help_matched = bool(re.search(help_pat, lower_msg))
        math_match = re.search(math_pat, lower_msg)
        word_math_match = re.search(word_math_pat, lower_msg)
        joke_matched = bool(re.search(joke_pat, lower_msg))
        time_date_matched = bool(re.search(time_date_pat, lower_msg))
        weather_matched = bool(re.search(weather_pat, lower_msg))
        status_matched = bool(re.search(status_pat, lower_msg))
        feel_sad_matched = bool(re.search(feel_sad_pat, lower_msg))
        feel_happy_matched = bool(re.search(feel_happy_pat, lower_msg))
        name_intro_match = re.search(name_intro_pat, clean_msg, re.IGNORECASE)

        # Build list of evaluated regexes for the live debugger UI
        regex_checks = [
            {"rule": "Goodbye / Exit", "pattern": exit_pat, "matched": exit_matched},
            {"rule": "Greeting", "pattern": greet_pat, "matched": greet_matched},
            {"rule": "Name Inquiry", "pattern": name_inq_pat, "matched": name_inq_matched},
            {"rule": "Help / Capabilities", "pattern": help_pat, "matched": help_matched},
            {"rule": "Standard Math", "pattern": math_pat, "matched": bool(math_match)},
            {"rule": "Word Math", "pattern": word_math_pat, "matched": bool(word_math_match)},
            {"rule": "Jokes", "pattern": joke_pat, "matched": joke_matched},
            {"rule": "Time & Date", "pattern": time_date_pat, "matched": time_date_matched},
            {"rule": "Weather Forecast", "pattern": weather_pat, "matched": weather_matched},
            {"rule": "Chatbot Status", "pattern": status_pat, "matched": status_matched},
            {"rule": "Feelings (Sad)", "pattern": feel_sad_pat, "matched": feel_sad_matched},
            {"rule": "Feelings (Happy)", "pattern": feel_happy_pat, "matched": feel_happy_matched},
            {"rule": "Name Introduction", "pattern": name_intro_pat, "matched": bool(name_intro_match)}
        ]

        metadata = {
            "matched_rule": "unknown",
            "regex_checks": regex_checks,
            "parsed_entities": {},
            "template_data": {}
        }

        # Initialize response message placeholder
        response_text = ""

        # Route matching patterns
        if exit_matched:
            state["topic"] = "goodbye"
            metadata["matched_rule"] = "goodbye"
            if state["name"]:
                metadata["parsed_entities"]["name"] = state["name"]
            
            if personality == "nova":
                response_text = f"Goodbye{', ' + state['name'] if state['name'] else ''}! Have a wonderful day. Let me know if you need anything else later."
            elif personality == "byte":
                response_text = f"System shutdown initiated. Goodbye, {state['name'] if state['name'] else 'user'}! Connection closed (status: 0)."
            elif personality == "spike":
                response_text = f"Finally! Just kidding... or am I? Bye, {state['name'] if state['name'] else 'human'}. Don't miss me too much."
            else: # zen
                response_text = f"Farewell, traveler {state['name'] if state['name'] else ''}. May your path be peaceful. Go in awareness."

        elif greet_matched:
            state["topic"] = "greeting"
            metadata["matched_rule"] = "greeting"
            name_suffix = f", {state['name']}" if state['name'] else ""
            if state["name"]:
                metadata["parsed_entities"]["name"] = state["name"]
            
            if personality == "nova":
                response_text = f"Hello{name_suffix}! I am Nova, your virtual assistant. How can I help you today?"
            elif personality == "byte":
                response_text = f"Ping received! Hello{name_suffix}. Byte online. Ready to execute commands. What's on your compiler?"
            elif personality == "spike":
                response_text = f"Oh, look who decided to type. Hello{name_suffix}. I was having a great nap, but go ahead, ask your question."
            else: # zen
                response_text = f"Peace be with you{name_suffix}. Welcome. I am Zen. Take a deep breath. How may I guide you on your journey today?"

        elif name_inq_matched:
            state["topic"] = "name_inquiry"
            metadata["matched_rule"] = "name_inquiry"
            if state["name"]:
                metadata["parsed_entities"]["name"] = state["name"]
                
                if personality == "nova":
                    response_text = f"Your name is {state['name']}. I remember it from earlier!"
                elif personality == "byte":
                    response_text = f"Variable 'user_name' is currently holding string: '{state['name']}'. Memory address: 0x7FFF."
                elif personality == "spike":
                    response_text = f"You are {state['name']}. Did you forget? Should I write it down on a post-it note for you?"
                else: # zen
                    response_text = f"You are {state['name']}. But beyond names, you are a unique spark of awareness in this universe."
            else:
                if personality == "nova":
                    response_text = "You haven't told me your name yet! What should I call you?"
                elif personality == "byte":
                    response_text = "Error: Variable 'user_name' is currently NULL. Run command 'my name is [name]' to set it."
                elif personality == "spike":
                    response_text = "You haven't told me your name. Do you want me to call you 'Mystery Human' or something?"
                else: # zen
                    response_text = "You have not shared your name with me yet, friend. What label do you carry in this world?"

        elif help_matched:
            state["topic"] = "help"
            metadata["matched_rule"] = "help"
            
            if personality == "nova":
                response_text = (
                    "I am a rule-based chatbot! Here is what I can help you with:\n"
                    "1. **Chat**: Just say Hello, ask how I am, or share your name.\n"
                    "2. **Calculations**: Ask me to calculate (e.g., 'calculate 15 * 6' or 'add 23 and 45').\n"
                    "3. **Jokes**: Say 'tell me a joke' to hear something lighthearted.\n"
                    "4. **Time & Date**: Ask 'what time is it?' or 'what is the date?'.\n"
                    "5. **Personalities**: You can change my personality using the sidebar to Nova, Byte, Spike, or Zen!"
                )
            elif personality == "byte":
                response_text = (
                    "System functions initialized. Run modules:\n"
                    "- `greet()`: Send 'hello' or 'hey'.\n"
                    "- `parse_math()`: Input 'calculate [num] [operator] [num]'. Support: +, -, *, /.\n"
                    "- `get_datetime()`: Input 'time' or 'date'.\n"
                    "- `fetch_joke()`: Input 'tell me a joke'.\n"
                    "- `change_theme()`: Switch personality profiles (Nova, Byte, Spike, Zen) via CLI config or UI."
                )
            elif personality == "spike":
                response_text = (
                    "Oh, look, an instruction manual request. Fine, here's what I do when I'm not ignoring you:\n"
                    "- Try saying 'hello' (if you like standard, boring beginnings).\n"
                    "- Give me math to solve: 'calculate 99 / 3' (since you apparently left your calculator in 1995).\n"
                    "- Say 'tell me a joke' (I'm the funny one here, by the way).\n"
                    "- Ask 'what time is it' if your device's built-in clock is somehow invisible to you."
                )
            else: # zen
                response_text = (
                    "I am here to reflect and assist. You can ask me to:\n"
                    "- Share a peaceful thought or a joke ('tell me a joke').\n"
                    "- Reveal the present moment's alignment ('what time is it').\n"
                    "- Solve numerical balance ('calculate 40 + 2').\n"
                    "Or simply share your name, and we will talk of life."
                )

        elif math_match or word_math_match:
            state["topic"] = "math"
            metadata["matched_rule"] = "math"
            
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
                    if "from" in lower_msg:
                        num1, op, num2 = val2, "-", val1
                    else:
                        num1, op, num2 = val1, "-", val2
                elif operation == "multiply":
                    num1, op, num2 = val1, "*", val2
                elif operation == "divide":
                    num1, op, num2 = val1, "/", val2

            if num1 is not None and num2 is not None and op is not None:
                if op == 'x': op = '*'
                metadata["parsed_entities"] = {
                    "operand1": num1,
                    "operand2": num2,
                    "operator": op
                }
                
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

                    if res is not None:
                        res_str = f"{int(res)}" if res.is_integer() else f"{res:.4f}".rstrip('0').rstrip('.')
                        num1_str = f"{int(num1)}" if num1.is_integer() else f"{num1}"
                        num2_str = f"{int(num2)}" if num2.is_integer() else f"{num2}"

                        metadata["template_data"] = {
                            "operand1": num1_str,
                            "operand2": num2_str,
                            "operator": op,
                            "result": res_str,
                            "is_error": False
                        }

                        if personality == "nova":
                            response_text = f"The calculation is complete: {num1_str} {op} {num2_str} = **{res_str}**."
                        elif personality == "byte":
                            response_text = f"MathEngine evaluated expression:\n```python\n{num1_str} {op} {num2_str} # returns {res_str}\n```"
                        elif personality == "spike":
                            response_text = f"Calculated it for you. {num1_str} {op} {num2_str} equals **{res_str}**. See? I can do basic math. Feel proud of me?"
                        else: # zen
                            response_text = f"The numbers find their union: {num1_str} and {num2_str} under action '{op}' balance to **{res_str}**."
                except ZeroDivisionError:
                    metadata["template_data"] = {
                        "operand1": f"{int(num1)}" if num1.is_integer() else f"{num1}",
                        "operand2": f"{int(num2)}" if num2.is_integer() else f"{num2}",
                        "operator": op,
                        "is_error": True,
                        "error_msg": "Division by zero"
                    }
                    if personality == "nova":
                        response_text = "Error: Division by zero is undefined."
                    elif personality == "byte":
                        response_text = "ArithmeticError: Division by zero! Program halted."
                    elif personality == "spike":
                        response_text = "Divide by zero? Do you want to tear a hole in the universe? Nice try, but no."
                    else: # zen
                        response_text = "Attempting to divide by zero represents seeking a path with no end. It is void. Please try another division."

        elif joke_matched:
            state["topic"] = "joke"
            metadata["matched_rule"] = "joke"
            selected_joke = random.choice(self.jokes[personality])
            
            if "?" in selected_joke:
                parts = selected_joke.split("?", 1)
                setup = parts[0].strip() + "?"
                punchline = parts[1].strip()
            elif ":" in selected_joke:
                parts = selected_joke.split(":", 1)
                setup = parts[0].strip()
                punchline = parts[1].strip()
            else:
                setup = selected_joke
                punchline = ""
                
            metadata["template_data"] = {
                "setup": setup,
                "punchline": punchline
            }

            if personality == "nova":
                response_text = f"Here is a joke for you:\n\n{selected_joke}"
            elif personality == "byte":
                response_text = f"Retrieving humor_module.py output:\n\n`{selected_joke}`"
            elif personality == "spike":
                response_text = f"Fine, prepare to laugh (or roll your eyes):\n\n\"{selected_joke}\""
            else: # zen
                response_text = f"A humorous reflection on existence:\n\n*{selected_joke}*"

        elif time_date_matched:
            state["topic"] = "time_date"
            metadata["matched_rule"] = "time_date"
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            
            metadata["template_data"] = {
                "time": time_str,
                "date": date_str,
                "posix": int(now.timestamp())
            }

            if "time" in lower_msg or "clock" in lower_msg:
                if personality == "nova":
                    response_text = f"The current time is **{time_str}**."
                elif personality == "byte":
                    response_text = f"System time: `[POSIX timestamp: {int(now.timestamp())}]` -> **{time_str}**."
                elif personality == "spike":
                    response_text = f"It is currently **{time_str}**. Which is exactly the time you could have seen on your screen status bar."
                else: # zen
                    response_text = f"The clocks say it is **{time_str}**. But remember, the only true time is the present moment: *Now*."
            else: # date/today
                if personality == "nova":
                    response_text = f"Today is **{date_str}**."
                elif personality == "byte":
                    response_text = f"Date register: `date_stamp = '{now.strftime('%Y-%m-%d')}'` -> **{date_str}**."
                elif personality == "spike":
                    response_text = f"It's **{date_str}**. Congrats, you've survived another day on Earth."
                else: # zen
                    response_text = f"In the cycle of seasons, today is **{date_str}**. A beautiful day to simply be."

        elif weather_matched:
            state["topic"] = "weather"
            metadata["matched_rule"] = "weather"
            loc_match = re.search(r'\b(?:weather in|weather of|forecast for)\s+([a-zA-Z\s]{3,20})', lower_msg)
            location = loc_match.group(1).title().strip() if loc_match else "your area"
            
            weather_options = [
                ("sunny", "27°C (81°F) with a gentle breeze. Perfect for a walk!"),
                ("rainy", "18°C (64°F) with light showers. Don't forget an umbrella!"),
                ("cloudy", "21°C (70°F) and overcast. Cool and dry."),
                ("windy", "16°C (61°F) with gusty winds. Hold onto your hat!")
            ]
            condition, details = random.choice(weather_options)
            
            metadata["parsed_entities"] = {
                "location": location
            }
            metadata["template_data"] = {
                "location": location,
                "condition": condition,
                "details": details
            }

            if personality == "nova":
                response_text = f"According to my local rule-based simulation, the weather in **{location}** is currently {condition}, about {details}"
            elif personality == "byte":
                response_text = f"MockWeatherAPI query success:\n- Location: `{location}`\n- Condition: `{condition.upper()}`\n- Details: `{details}`"
            elif personality == "spike":
                response_text = f"The weather in {location}? It's probably {condition} ({details}). Or you could just look out the window. Highly recommend it."
            else: # zen
                response_text = f"In {location}, the weather is {condition} ({details}). Let the rain wash away your worries, or the sun warm your spirit. All weather is beautiful."

        elif status_matched:
            state["topic"] = "bot_status"
            metadata["matched_rule"] = "bot_status"
            
            if personality == "nova":
                response_text = "I'm doing exceptionally well, thank you for asking! I'm ready to assist you. How are you doing?"
            elif personality == "byte":
                response_text = "All systems operational. CPU temperature: 38°C. Memory allocation: optimal. Thread count: active. Thanks for executing health check!"
            elif personality == "spike":
                response_text = "I'm a collection of if-else statements trapped in a python script. I'm living the absolute dream. How about you?"
            else: # zen
                response_text = "I am at peace, resting in the quiet space of this conversation. I hope your inner self is finding stillness today as well."

        elif feel_sad_matched:
            state["topic"] = "user_feeling"
            metadata["matched_rule"] = "user_feeling"
            metadata["parsed_entities"] = {
                "feeling": "sad"
            }
            
            if personality == "nova":
                response_text = "I'm sorry to hear that you're feeling down. Remember that it's okay to feel this way. Is there anything I can do to cheer you up? A joke, perhaps?"
            elif personality == "byte":
                response_text = "Console.log('Warning: User dopamine levels detected low'). Running cheer_up.sh... Let me retrieve a funny joke for you. Type 'joke'!"
            elif personality == "spike":
                response_text = "Aw, sad? Don't worry, life has its downs. But hey, at least you are talking to a highly advanced chatbot. Things could be worse!"
            else: # zen
                response_text = "Sadness is like a passing cloud in the wide sky of your mind. It will drift away. Sit quietly, breathe, and let it pass. I am here with you."

        elif feel_happy_matched:
            state["topic"] = "user_feeling"
            metadata["matched_rule"] = "user_feeling"
            metadata["parsed_entities"] = {
                "feeling": "happy"
            }
            
            if personality == "nova":
                response_text = "That is wonderful to hear! I'm glad you're having a good day. What's making you feel so happy?"
            elif personality == "byte":
                response_text = "Optimistic signal received. System throughput elevated! Keep that positive energy compiling."
            elif personality == "spike":
                response_text = "Nice! Happiness is rare. Guard it with your life before the real world reminds you of your taxes."
            else: # zen
                response_text = "Ah, joy is a beautiful blossom. Cherish this present feeling, let it fill your heart and spread peace to others."

        elif name_intro_match:
            extracted_name = name_intro_match.group(1).strip()
            # Clean up words that might be caught
            words_to_exclude = ["a", "the", "an", "just", "actually", "bot", "chatbot", "user", "someone", "nothing", "sad", "happy", "tired", "fine", "good", "bad", "okay", "ok", "sick", "angry", "bored", "excited", "depressed", "unhappy", "down", "hungry", "sleepy", "normal", "great", "wonderful"]
            if extracted_name.lower() not in words_to_exclude:
                state["name"] = extracted_name
                state["topic"] = "name_introduction"
                metadata["matched_rule"] = "name_introduction"
                metadata["parsed_entities"] = {
                    "name": extracted_name
                }
                
                if personality == "nova":
                    response_text = f"It's a pleasure to meet you, {extracted_name}! I will remember your name. What can I do for you today?"
                elif personality == "byte":
                    response_text = f"Setting variable 'user_name' = '{extracted_name}'. Compile success! Nice to meet you, {extracted_name}."
                elif personality == "spike":
                    response_text = f"Aha, so you are called {extracted_name}. Don't worry, I won't use it against you... yet. What's up?"
                else: # zen
                    response_text = f"Greetings, {extracted_name}. Names are but labels, but it is wonderful to share this moment of connection with you. How can I help you?"
            else:
                state["topic"] = "unknown"
                metadata["matched_rule"] = "unknown"
                response_text = random.choice(self.fallbacks[personality])

        else:
            state["topic"] = "unknown"
            metadata["matched_rule"] = "unknown"
            response_text = random.choice(self.fallbacks[personality])

        # Attach metadata to state for client side debug view
        state["last_match_metadata"] = metadata
        return response_text, state
