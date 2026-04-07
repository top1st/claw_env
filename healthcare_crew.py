from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import pandas as pd
from datetime import datetime
import os

# ============ DEFINE AGENTS ============

class HealthcareCrew:
    def __init__(self, extracted_data=None):
        self.data = extracted_data
        self.agents = []
        self.tasks = []
    
    def create_agents(self):
        """Create specialized AI agents"""
        
        # Agent 1: Data Quality Specialist
        quality_agent = Agent(
            role="Data Quality Specialist",
            goal="Validate and clean healthcare staff data",
            backstory="""You have 10 years of experience in healthcare data governance.
            You spot anomalies, missing fields, and formatting issues instantly.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Agent 2: Operations Analyst  
        ops_agent = Agent(
            role="Healthcare Operations Analyst",
            goal="Analyze staffing patterns and identify gaps",
            backstory="""You optimize hospital staffing. You know what ratios are safe
            and where understaffing creates risk.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Agent 3: Report Writer
        report_agent = Agent(
            role="Clinical Report Writer",
            goal="Create clear, actionable reports for management",
            backstory="""You translate technical data into executive summaries.
            Your reports are known for being concise and useful.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 4: Compliance Checker
        compliance_agent = Agent(
            role="Healthcare Compliance Officer",
            goal="Ensure data meets regulatory standards",
            backstory="""You enforce HIPAA and healthcare data standards.
            You flag any compliance risks immediately.""",
            verbose=True,
            allow_delegation=True
        )
        
        self.agents = [quality_agent, ops_agent, report_agent, compliance_agent]
        return self.agents
    
    def create_tasks(self):
        """Create tasks for each agent"""
        
        if not self.data or len(self.data) == 0:
            print("❌ No data available for tasks")
            return []
        
        # Convert data to string for agents
        data_summary = f"""
        Healthcare Staff Data:
        Total Records: {len(self.data)}
        Sample: {self.data.head(3).to_string()}
        Columns: {list(self.data.columns)}
        """
        
        # Task 1: Quality Check
        quality_task = Task(
            description=f"""
            Analyze this healthcare staff data for data quality issues:
            
            {data_summary}
            
            Identify:
            1. Missing or null values
            2. Inconsistent formatting
            3. Duplicate records
            4. Invalid data patterns
            
            Provide a quality score (0-100%) and specific fixes.
            """,
            expected_output="Data quality report with score and fix recommendations",
            agent=self.agents[0]
        )
        
        # Task 2: Operations Analysis
        ops_task = Task(
            description=f"""
            Based on this staff data:
            
            {data_summary}
            
            Provide:
            1. Staffing summary by role
            2. Identify any critical gaps
            3. Recommend optimal staffing levels
            4. Note any scheduling risks
            """,
            expected_output="Staffing analysis with gap identification",
            agent=self.agents[1]
        )
        
        # Task 3: Compliance Check
        compliance_task = Task(
            description=f"""
            Review this data for compliance issues:
            
            {data_summary}
            
            Check for:
            1. PII exposure risks
            2. Missing mandatory fields
            3. Format standard violations
            4. Data retention concerns
            """,
            expected_output="Compliance status report",
            agent=self.agents[3]
        )
        
        # Task 4: Final Report (depends on previous tasks)
        report_task = Task(
            description="""
            Create an executive summary report combining:
            - Data quality findings
            - Operations analysis  
            - Compliance status
            
            Format as a professional healthcare report with:
            - Executive summary (2-3 sentences)
            - Key findings (bulleted list)
            - Action items (prioritized)
            - Risk assessment (High/Medium/Low)
            """,
            expected_output="Final formatted healthcare report",
            agent=self.agents[2],
            context=[quality_task, ops_task, compliance_task]  # Depends on these
        )
        
        self.tasks = [quality_task, ops_task, compliance_task, report_task]
        return self.tasks
    
    def run_crew(self):
        """Execute the crew of agents"""
        print("\n" + "="*60)
        print("🤖 CREWAI HEALTHCARE AGENTS STARTING")
        print("="*60)
        
        self.create_agents()
        self.create_tasks()
        
        # Create the crew
        crew = Crew(
            agents=self.agents, # type: ignore
            tasks=self.tasks,
            process=Process.sequential,  # Tasks run in order
            verbose=True
        )
        
        print("\n🚀 Running multi-agent analysis...")
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("✅ CREWAI ANALYSIS COMPLETE")
        print("="*60)
        
        return result

# ============ INTEGRATION WITH YOUR SCRAPER ============

def run_complete_pipeline():
    """End-to-end: Scrape → AI Agents → Report"""
    
    # Step 1: Run your existing scraper
    from healthcare_automation import HealthcareAutomation
    
    print("📊 STEP 1: Scraping healthcare portal...")
    scraper = HealthcareAutomation(headless=True)
    
    try:
        scraper.login()
        scraper.navigate_to_employees()
        data = scraper.extract_data()
        scraper.save_reports(data)
        
        print(f"✅ Extracted {len(data)} records")
        
        # Step 2: Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Step 3: Run CrewAI agents
        crew_system = HealthcareCrew(extracted_data=df)
        analysis_result = crew_system.run_crew()
        
        # Step 4: Save final report
        with open("crewai_final_report.txt", "w", encoding="utf-8") as f:
            f.write(str(analysis_result))
        
        print("\n📁 Final report saved: crewai_final_report.txt")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    # Run with existing data
    if os.path.exists("staff_report.xlsx"):
        df = pd.read_excel("staff_report.xlsx")
        crew = HealthcareCrew(extracted_data=df)
        result = crew.run_crew()
        print(result)
    else:
        print("No data found. Run scraper first.")