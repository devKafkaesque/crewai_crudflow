from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
import os
from crewai import LLM
from dotenv import load_dotenv
load_dotenv()

@CrewBase
class chatbot_crew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    llm = LLM(
        model=os.getenv("model"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    SearchTool = SerperDevTool()
    
    @agent
    def information_handler(self) -> Agent:
        return Agent(
            config=self.agents_config["information_handler"],
        )
    
    @agent
    def crud_handler(self) -> Agent:
        return Agent(
            config=self.agents_config["crud_handler"],
        )

    @task
    def extract_data(self) -> Task:
        task_config = self.tasks_config["extract_data"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.information_handler()
        )
    
    @task
    def perform_crud(self) -> Task:
        task_config = self.tasks_config["perform_crud"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.crud_handler()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            llm=self.llm,
            verbose=False
        )