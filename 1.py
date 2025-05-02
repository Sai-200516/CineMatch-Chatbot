from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Create chatbot
chatbot = ChatBot('MyBot')

# Train chatbot
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")

# Chat loop
while True:
    user_input = input("You: ")
    response = chatbot.get_response(user_input)
    print(f"MyBot: {response}")
