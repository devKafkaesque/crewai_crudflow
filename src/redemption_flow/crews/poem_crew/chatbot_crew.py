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
        model = os.getenv("model"),
        api_key = os.getenv("OPENAI_API_KEY")
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
        return Task(
            config=self.tasks_config["extract_data"],
        )
    
    @task
    def perform_crud(self) -> Task:
        return Task(
            config=self.tasks_config["perform_crud"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            llm=self.llm,
            verbose=False
        )
