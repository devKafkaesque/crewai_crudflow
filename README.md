# InsuranceBotFlow

A CrewAI-powered insurance chatbot that processes user queries related to insurance claims.

## Overview

InsuranceBotFlow is an AI-powered chatbot application built with CrewAI that helps users interact with their insurance claims data. The system can process natural language queries to retrieve claim information and is designed to be extensible for additional insurance-related operations.

## Features

- **Insurance-Specific Interactions**: Processes only insurance-related queries.
- **Claim Management**: View existing claims in the database.
- **Policy Lookup**: Check claim details by policy number.
- **Natural Language Processing**: Understands user intent through AI-powered analysis.

## Current Capabilities

- **List All Claims**: Returns all claims in the database.
- **Check Specific Claims**: Retrieves claim details by policy number.
- **Filter Non-Insurance Queries**: Rejects queries not related to insurance.

## Database Structure

The application uses an SQLite database (`insurance.db`) with a `claims` table that contains:

- `id`
- `policy_number`
- `claim_amount`
- `claim_date`
- `status`

## Usage Examples

### Working Queries

- "list all claims"
- "check claim with policy number: POL456"

### Non-Working Queries (Need Implementation)

- "create new claim as {'policy_number': 'POL789', 'claim_amount': 750.0, 'claim_date': '2025-03-25', 'status': 'pending'}"
- "check policy number POL456" (currently returns "Unsupported operation: unknown")

## Project Structure

- `main.py`: Contains the `InsuranceBotFlow` class and main application logic.
- `chatbot_crew.py`: Defines the CrewAI agents and tasks for processing user queries.
- `config/`: Configuration files for agents and tasks.
- `insurance.db`: SQLite database storing claim information.

## Future Enhancements

- Implement create, update, and delete operations for claims.
- Handle policy-related questions.
- Improve natural language understanding.

## Requirements

- Python 3.8+
- CrewAI
- SQLite3
- OpenAI API key (for the LLM)

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a .env file with your OpenAI API key and model configuration. For example:
     ```bash
     OPENAI_API_KEY=your_api_key_here
     MODEL_NAME=gpt-3.5-turbo
     ```
   - Replace your_api_key_here with your actual OpenAI API key and adjust MODEL_NAME to your preferred model (e.g., gpt-3.5-turbo or gpt-4).
4. Initialize and Reconfigure the database(according to requirements):
   - Run the database initialization script if provided (e.g., python init_db.py). Check the project documentation or code for exact instructions.
5. Run the application:
   ```bash
   crewai run
   ```
## Notes
The current implementation may display Pydantic V1 style deprecation warnings. To suppress these, add the following code to your project:
  ```python
  import warnings
  from pydantic import PydanticDeprecatedSince20
  warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
  ```
