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
                elif ("check" in user_input_lower or "details" in user_input_lower) and "policy number" in user_input_lower:
                    match = re.search(r"POL\d+", user_input)
                    policy_number = match.group(0) if match else None
                    if policy_number:
                        result = {"operation": "read", "table": "claims", "policy_number": policy_number, "query": user_input}
                    else:
                        result = {"operation": "unknown", "query": user_input}
                elif "update" in user_input_lower:
                    match = re.search(r"update claim (\d+) status to (\w+)", user_input)
                    if match:
                        claim_id = int(match.group(1))
                        status = match.group(2)
                        result = {"operation": "update", "table": "claims", "claim_id": claim_id, "status": status, "query": user_input}
                    else:
                        result = {"operation": "unknown", "query": user_input}
                elif "create" in user_input_lower or "new" in user_input_lower or "add" in user_input_lower:
                    try:
                        # Extract the JSON-like data from the input
                        import ast
                        match = re.search(r'\{.*\}', user_input)
                        if match:
                            claim_data = ast.literal_eval(match.group(0))
                            result = {
                                "operation": "create", 
                                "table": "claims", 
                                "data": claim_data,
                                "query": user_input
                            }
                        else:
                            result = {"operation": "unknown", "query": user_input}
                    except Exception as e:
                        print(f"Error parsing claim data: {e}")
                        result = {"operation": "unknown", "query": user_input}
                elif "delete" in user_input_lower:
                    match = re.search(r"delete claim with id (\d+)", user_input)
                    if match:
                        claim_id = int(match.group(1))
                        result = {"operation": "delete", "table": "claims", "claim_id": claim_id, "query": user_input}
                    else:
                        result = {"operation": "unknown", "query": user_input}
                elif any(keyword in user_input_lower for keyword in ['policy', 'coverage', 'terms', 'conditions', 'premium', 'deductible']):
                    result = {"operation": "policy_info", "query": user_input}
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
        claim_id = extracted_data.get("claim_id")
        status = extracted_data.get("status")
        
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
            
            elif operation == "create" and table == "claims":
                data = extracted_data.get("data", {})
                
                required_fields = ["policy_number", "claim_amount", "claim_date", "status"]
                if not all(field in data for field in required_fields):
                    return {"status": "error", "message": "Missing required fields for claim creation"}
                
                cursor.execute(
                    "INSERT INTO claims (policy_number, claim_amount, claim_date, status) VALUES (?, ?, ?, ?)",
                    (data["policy_number"], data["claim_amount"], data["claim_date"], data["status"])
                )
                
                conn.commit()
                new_id = cursor.lastrowid
                
                return {
                    "status": "success", 
                    "message": f"Claim created successfully with ID: {new_id}",
                    "claim_id": new_id
                }
            
            elif operation == "update" and table == "claims":
                if claim_id and status:
                    cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
                    if cursor.fetchone():
                        cursor.execute(
                            "UPDATE claims SET status = ? WHERE id = ?",
                            (status, claim_id)
                        )
                        conn.commit()
                        return {
                            "status": "success", 
                            "message": f"Claim {claim_id} status updated to {status}"
                        }
                    else:
                        return {"status": "error", "message": f"Claim {claim_id} does not exist"}
                else:
                    return {"status": "error", "message": "Missing claim ID or status for update"}
            
            elif operation == "delete" and table == "claims":
                if claim_id:
                    cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
                    if cursor.fetchone():
                        cursor.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
                        conn.commit()
                        return {
                            "status": "success", 
                            "message": f"Claim {claim_id} deleted successfully"
                        }
                    else:
                        return {"status": "error", "message": f"Claim {claim_id} does not exist"}
                else:
                    return {"status": "error", "message": "Missing claim ID for deletion"}
            
            elif operation == "policy_info":
                # Fetch policy information from a database or knowledge base
                # For demonstration, return a static message
                return {"status": "success", "message": "Policy information is available upon request."}
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
