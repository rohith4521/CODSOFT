import unittest
from chatbot import Chatbot

class TestChatbotEngine(unittest.TestCase):
    def setUp(self):
        self.bot = Chatbot()

    def test_greetings(self):
        state = {}
        for greeting in ["hello", "hi", "hey", "good morning"]:
            res, state = self.bot.process_message(greeting, state, "nova")
            self.assertIn("Hello", res)
            self.assertEqual(state["topic"], "greeting")

    def test_name_introduction_and_inquiry(self):
        state = {}
        # Nova introduction
        res, state = self.bot.process_message("My name is John Doe", state, "nova")
        self.assertEqual(state["name"], "John Doe")
        self.assertIn("John Doe", res)
        self.assertEqual(state["topic"], "name_introduction")

        # Inquiry check
        res, state = self.bot.process_message("What is my name?", state, "nova")
        self.assertIn("John Doe", res)
        self.assertEqual(state["topic"], "name_inquiry")

        # Byte introduction
        state = {}
        res, state = self.bot.process_message("Call me HackerOne", state, "byte")
        self.assertEqual(state["name"], "HackerOne")
        self.assertIn("HackerOne", res)
        
    def test_calculator(self):
        state = {}
        # Test standard math regex
        res, state = self.bot.process_message("calculate 12 * 8", state, "nova")
        self.assertIn("12 * 8 = **96**", res)
        self.assertEqual(state["topic"], "math")

        # Test word math regex
        res, state = self.bot.process_message("add 45 and 15", state, "nova")
        self.assertIn("45 + 15 = **60**", res)

        # Test divide by zero safety
        res, state = self.bot.process_message("calculate 50 / 0", state, "nova")
        self.assertIn("Error: Division by zero", res)

        # Test decimal math
        res, state = self.bot.process_message("calculate 10.5 - 2.5", state, "nova")
        self.assertIn("10.5 - 2.5 = **8**", res)

    def test_time_and_date(self):
        state = {}
        res, state = self.bot.process_message("What time is it?", state, "nova")
        self.assertIn("time is", res.lower())
        self.assertEqual(state["topic"], "time_date")

        res, state = self.bot.process_message("What is today's date?", state, "nova")
        self.assertIn("today is", res.lower())
        
    def test_jokes(self):
        state = {}
        res, state = self.bot.process_message("tell me a joke", state, "nova")
        self.assertTrue(len(res) > 5)
        self.assertEqual(state["topic"], "joke")

    def test_user_feelings(self):
        state = {}
        res, state = self.bot.process_message("i am sad", state, "nova")
        self.assertIn("sorry", res.lower())
        self.assertEqual(state["topic"], "user_feeling")

        res, state = self.bot.process_message("I'm feeling excited!", state, "nova")
        self.assertIn("wonderful", res.lower())
        
    def test_personality_differences(self):
        # Greetings in different personalities should have distinct flags/phrases
        state = {}
        res_nova, _ = self.bot.process_message("hello", state, "nova")
        res_byte, _ = self.bot.process_message("hello", state, "byte")
        res_spike, _ = self.bot.process_message("hello", state, "spike")
        res_zen, _ = self.bot.process_message("hello", state, "zen")

        self.assertIn("Nova", res_nova)
        self.assertIn("Byte online", res_byte)
        self.assertIn("nap", res_spike) # Spike complains about nap
        self.assertIn("Peace be with you", res_zen)

if __name__ == "__main__":
    unittest.main()
