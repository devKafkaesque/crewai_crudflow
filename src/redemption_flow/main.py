#!/usr/bin/env python
from crewai.flow import Flow, start, listen, router
from numpy import outer
from redemption_flow.crews.poem_crew.chatbot_crew import chatbot_crew

class InsuranceBotFlow(Flow):
    insurance_terms = [
        'claim', 'policy', 'premium', 'deductible', 'coverage',
        'beneficiary', 'endorsement', 'exclusion', 'underwriting',
        'adjuster', 'agent', 'broker', 'insurer', 'insured'
    ]
    @start()
    def user_input_from_chatbot(self, inputs):
        user_input = inputs["user_input"]
        if any(term in user_input.lower() for term in self.insurance_terms):
            return user_input
        else:
            print("I'm sorry, I can only help with insurance-related queries.")
            return None

    @listen(user_input_from_chatbot)
    def extract_data(self, user_input):
        if user_input is not None:
            print("Extracting Data")
            result = (chatbot_crew.crew().kickoff(inputs={"user_input": user_input}))
            print("Data Extracted:", result)
            return result
        return None

    @listen(extract_data)
    def crud_operator(self, extracted_data):
        if extracted_data is not None:
            print("Performing CRUD operations on the extracted data...")
            task = chatbot_crew.perform_crud()
            agent = chatbot_crew.crud_handler()
            result = agent.execute_task(task, inputs={"extracted_data": extracted_data})
            print("CRUD operations performed:", result)
            return result
        return None

if __name__ == "__main__":
    while True:
        user_input = input("Enter your input: ")
        if user_input.lower() == "exit":
            break
        flow = InsuranceBotFlow()
        flow.kickoff(inputs={"user_input": user_input})