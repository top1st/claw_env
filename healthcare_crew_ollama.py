# healthcare_crew_fixed.py
import os
import pandas as pd
from datetime import datetime
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process

# ============ CONFIGURE OLLAMA FOR CREWAI ============
# This tells CrewAI to use your local Ollama instead of OpenAI
class OllamaLLM:
    """Wrapper to make Ollama compatible with CrewAI"""
    
    def __init__(self, model="phi3", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.llm = Ollama(model=model, base_url=base_url)
    
    def call(self, prompt, temperature=0.3):
        """Call the Ollama model"""
        return self.llm.invoke(prompt)
    
    def __call__(self, prompt, **kwargs):
        return self.call(prompt, **kwargs)

# Initialize Ollama LLM
ollama_llm = OllamaLLM(model="phi3")  # or "mistral", "llama2"

# ============ CREATE AGENTS WITH OLLAMA ============

class HealthcareCrew:
    def __init__(self, extracted_data=None):
        self.data = extracted_data
        self.agents = []
        self.tasks = []
    
    def create_agents(self):
        """Create specialized AI agents using Ollama"""
        
        # Agent 1: Data Quality Specialist
        quality_agent = Agent(
            role="Data Quality Specialist",
            goal="Validate and clean healthcare staff data",
            backstory="You have 10 years of experience in healthcare data governance. You spot anomalies instantly.",
            verbose=True,
            allow_delegation=True,
            llm=ollama_llm.llm  # Use Ollama instead of OpenAI
        )
        
        # Agent 2: Operations Analyst
        ops_agent = Agent(
            role="Healthcare Operations Analyst",
            goal="Analyze staffing patterns and identify gaps",
            backstory="You optimize hospital staffing and identify understaffing risks.",
            verbose=True,
            allow_delegation=True,
            llm=ollama_llm.llm
        )
        
        # Agent 3: Report Writer
        report_agent = Agent(
            role="Clinical Report Writer",
            goal="Create clear, actionable reports for management",
            backstory="You translate technical data into executive summaries.",
            verbose=True,
            allow_delegation=False,
            llm=ollama_llm.llm
        )
        
        self.agents = [quality_agent, ops_agent, report_agent]
        return self.agents
    
    def create_tasks(self):
        """Create tasks for each agent"""
        
        if self.data is None or len(self.data) == 0:
            print("❌ No data available")
            return []
        
        # Format data for agents
        data_text = self.data.to_string(index=False)
        
        # Task 1: Quality Check
        quality_task = Task(
            description=f"""
            Analyze this healthcare staff data for quality issues:
            
            {data_text}
            
            Identify:
            1. Missing or null values
            2. Inconsistent formatting
            3. Duplicate records
            
            Provide a quality score (0-100%).
            """,
            expected_output="Data quality report with score and issues",
            agent=self.agents[0]
        )
        
        # Task 2: Operations Analysis
        ops_task = Task(
            description=f"""
            Based on this staff data:
            
            {data_text}
            
            Provide:
            1. Staffing summary
            2. Any critical gaps
            3. Recommendations
            """,
            expected_output="Staffing analysis with recommendations",
            agent=self.agents[1]
        )
        
        # Task 3: Final Report (depends on previous tasks)
        report_task = Task(
            description="""
            Create an executive summary combining:
            - Data quality findings
            - Operations analysis
            
            Format as a professional report with:
            - Executive summary
            - Key findings (bulleted list)
            - Action items
            """,
            expected_output="Final formatted healthcare report",
            agent=self.agents[2],
            context=[quality_task, ops_task]
        )
        
        self.tasks = [quality_task, ops_task, report_task]
        return self.tasks
    
    def run_crew(self):
        """Execute the crew of agents"""
        print("\n" + "="*60)
        print("🤖 CREWAI WITH OLLAMA - HEALTHCARE AGENTS")
        print("="*60)
        
        self.create_agents()
        self.create_tasks()
        
        # Create the crew
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Running multi-agent analysis with Ollama...")
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("✅ CREWAI ANALYSIS COMPLETE")
        print("="*60)
        
        return result

# ============ SIMPLER VERSION (NO EXTERNAL DEPENDENCIES) ============

class SimpleCrewWithOllama:
    """
    A simpler implementation that doesn't require CrewAI's complex LLM setup.
    This demonstrates the multi-agent pattern using direct Ollama calls.
    """
    
    def __init__(self, data_df):
        self.data = data_df
        self.ollama_model = "phi3"  # Change to your model
        
    def call_ollama(self, prompt):
        """Direct call to Ollama"""
        import requests
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 300}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    
    def agent_quality_check(self):
        """Agent 1: Quality Specialist"""
        print("\n🔍 Agent 1 (Quality Specialist): Analyzing data quality...")
        
        data_text = self.data.to_string(index=False)
        prompt = f"""
        You are a healthcare data quality specialist.
        Analyze this staff data and list ONLY issues (missing data, bad formatting, duplicates):
        
        {data_text}
        
        Also give a quality score out of 100.
        Keep response under 150 words.
        """
        
        return self.call_ollama(prompt)
    
    def agent_ops_analysis(self):
        """Agent 2: Operations Analyst"""
        print("\n📊 Agent 2 (Operations Analyst): Analyzing staffing...")
        
        data_text = self.data.to_string(index=False)
        prompt = f"""
        You are a healthcare operations analyst.
        Based on this staff data:
        
        {data_text}
        
        Provide:
        1. Total staff count
        2. One key observation
        3. One recommendation
        
        Keep response under 150 words.
        """
        
        return self.call_ollama(prompt)
    
    def agent_report_writer(self, quality_report, ops_report):
        """Agent 3: Report Writer"""
        print("\n📝 Agent 3 (Report Writer): Creating final report...")
        
        prompt = f"""
        You are a healthcare report writer.
        Combine these two analyses into ONE professional report:
        
        QUALITY ANALYSIS:
        {quality_report}
        
        OPERATIONS ANALYSIS:
        {ops_report}
        
        Format as:
        EXECUTIVE SUMMARY (2 sentences)
        KEY FINDINGS (bulleted list)
        RECOMMENDATIONS (numbered list)
        """
        
        return self.call_ollama(prompt)
    
    def run_full_crew(self):
        """Run all agents in sequence"""
        print("\n" + "="*60)
        print("🤖 MULTI-AGENT SYSTEM WITH OLLAMA")
        print("="*60)
        
        # Agent 1
        quality = self.agent_quality_check()
        print(f"\n📋 Quality Report:\n{quality}")
        
        # Agent 2
        ops = self.agent_ops_analysis()
        print(f"\n📋 Operations Report:\n{ops}")
        
        # Agent 3 (depends on previous)
        final_report = self.agent_report_writer(quality, ops)
        
        # Save everything
        with open("multi_agent_report.txt", "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("MULTI-AGENT HEALTHCARE REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write("FINAL REPORT:\n")
            f.write(final_report)
            f.write("\n\n" + "="*60 + "\n")
            f.write("DETAILS:\n\n")
            f.write("QUALITY ANALYSIS:\n" + quality + "\n\n")
            f.write("OPERATIONS ANALYSIS:\n" + ops + "\n")
        
        print("\n" + "="*60)
        print("✅ FINAL REPORT:")
        print("="*60)
        print(final_report)
        print("\n📁 Saved: multi_agent_report.txt")
        
        return final_report

# ============ RUN ============
if __name__ == "__main__":
    # Load your extracted data
    try:
        df = pd.read_excel("staff_report.xlsx")
        print(f"✅ Loaded {len(df)} records from staff_report.xlsx")
        print(df.head())
        
        # Use the simpler version that definitely works with Ollama
        crew = SimpleCrewWithOllama(df)
        report = crew.run_full_crew()
        
    except FileNotFoundError:
        print("❌ staff_report.xlsx not found")
        print("   Run your scraper first to extract data")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure Ollama is running: ollama serve")