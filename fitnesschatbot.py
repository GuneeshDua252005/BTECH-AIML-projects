import openai

# Set OpenAI API key
openai.api_key = "YOUR_API_KEY"

# Function to get a response from OpenAI for fitness advice
def get_fitness_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Function to generate workout plan based on fitness level
def generate_workout_plan(level="beginner"):
    workout_plan = {
        "beginner": [
            "Push-ups: 3 sets of 10 reps",
            "Bodyweight Squats: 3 sets of 15 reps",
            "Plank: 3 sets of 30 seconds",
            "Jogging: 15-20 minutes"
        ],
        "intermediate": [
            "Push-ups: 4 sets of 15 reps",
            "Squats: 4 sets of 20 reps",
            "Plank: 3 sets of 45 seconds",
            "Running: 20-30 minutes"
        ],
        "advanced": [
            "Push-ups: 5 sets of 20 reps",
            "Weighted Squats: 4 sets of 15 reps",
            "Plank: 4 sets of 1 minute",
            "Running: 30-45 minutes"
        ]
    }
    return workout_plan.get(level, workout_plan["beginner"])

# User progress dictionary to track goals and workouts completed
user_progress = {
    "workouts_completed": 0,
    "goals": "Run 5 km in 30 minutes"
}

# Function to update user progress
def update_progress():
    user_progress["workouts_completed"] += 1
    return f"Great job! You've now completed {user_progress['workouts_completed']} workouts."

# Main fitness chatbot function
def fitness_chatbot():
    print("Welcome to the Fitness Coach Chatbot!")
    print("Commands: 'workout', 'progress', 'advice', 'exit'")

    while True:
        user_input = input("You: ").lower()

        if user_input == "exit":
            print("Goodbye! Keep up the great work!")
            break
        elif user_input == "workout":
            level = input("Enter your fitness level (beginner/intermediate/advanced): ").strip().lower()
            workout_plan = generate_workout_plan(level)
            print("Your workout plan:")
            for exercise in workout_plan:
                print(f"- {exercise}")
        elif user_input == "progress":
            print(update_progress())
            print(f"Current goal: {user_progress['goals']}")
        elif user_input == "advice":
            question = input("Ask for fitness advice: ")
            response = get_fitness_response(question)
            print("Advice:", response)
        else:
            print("Invalid command. Try again.")

# Run the chatbot
fitness_chatbot()