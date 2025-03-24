#!/usr/bin/env python
import sqlite3
from crewai.flow import Flow, start, listen
from redemption_flow.crews.poem_crew.chatbot_crew import chatbot_crew
import re

class InsuranceBotFlow(Flow):
    insurance_terms = [
        'claim', 'policy', 'premium', 'deductible', 'coverage',
        'beneficiary', 'endorsement', 'exclusion', 'underwriting',
        'adjuster', 'agent', 'broker', 'insurer', 'insured'
    ]

    @start()
    def user_input_from_chatbot(self):
        print(self.state)
        if any(term in self.state['user_input'].lower() for term in self.insurance_terms):
            return self.state['user_input']
        else:
            print("I'm sorry, I can only help with insurance-related queries.")
            return None

    @listen(user_input_from_chatbot)
    def extract_data(self, user_input):
        if user_input is not None:
            print("Extracting Data")
            chatbot_instance = chatbot_crew()
            result = chatbot_instance.crew().kickoff(inputs={"user_input": user_input})
            
            if not isinstance(result, dict):
                user_input_lower = user_input.lower()
                if "list" in user_input_lower and "claims" in user_input_lower:
                    result = {"operation": "read", "table": "claims", "query": user_input}
                elif "details" in user_input_lower and "policy number" in user_input_lower:
                    match = re.search(r"'([^']+)'", user_input)
                    policy_number = match.group(1) if match else None
                    if policy_number:
                        result = {"operation": "read", "table": "claims", "policy_number": policy_number, "query": user_input}
                    else:
                        result = {"operation": "unknown", "query": user_input}
                else:
                    result = {"operation": "unknown", "query": user_input}
            print("Data Extracted:", result)
            return result
        return None

    @listen(extract_data)
    def crud_operator(self, extracted_data):
        if extracted_data is not None:
            print("Performing CRUD operations on the extracted data...")
            result = self._perform_db_operation(extracted_data)
            print("CRUD operations performed:", result)
            return result
        return None

    def _perform_db_operation(self, extracted_data):
        operation = extracted_data.get("operation", "read")
        table = extracted_data.get("table", "claims")
        policy_number = extracted_data.get("policy_number")
        
        try:
            conn = sqlite3.connect("insurance.db")
            cursor = conn.cursor()
            
            if operation == "read" and table == "claims":
                if policy_number:
                    cursor.execute("SELECT * FROM claims WHERE policy_number = ?", (policy_number,))
                else:
                    cursor.execute("SELECT * FROM claims")
                
                claims = cursor.fetchall()
                if claims:
                    return {"status": "success", "claims": [dict(zip(["id", "policy_number", "claim_amount", "claim_date", "status"], claim)) for claim in claims]}
                else:
                    return {"status": "success", "claims": [], "message": f"No claims found for policy number '{policy_number}'" if policy_number else "No claims found."}
            else:
                return {"status": "error", "message": f"Unsupported operation: {operation}"}
                
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        finally:
            if conn:
                conn.close()

def kickoff():
    while True:
        user_input = input("Enter your input: ")
        if user_input.lower() == "exit":
            break
        flow = InsuranceBotFlow()
        flow.kickoff(inputs={"user_input": user_input})

if __name__ == "__main__":
    kickoff()