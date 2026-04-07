import requests
import json
import pandas as pd
import os
from datetime import datetime

# Ollama API endpoint (default)
OLLAMA_API = "http://localhost:11434/api/generate"

class OllamaReporter:
    def __init__(self, model="phi3"):
        """
        Initialize with local Ollama model
        Popular options: phi3 (fastest), mistral (balanced), llama3.2 (small)
        """
        self.model = model
        self.base_url = "http://localhost:11434"
        
    def check_ollama(self):
        """Verify Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama running. Available models:")
                for m in models:
                    print(f"   - {m['name']}")
                return True
        except:
            print("❌ Ollama not running. Start with: ollama serve")
            return False
    
    def generate(self, prompt, system_prompt=None, temperature=0.3):
        """
        Call Ollama with a prompt
        temperature: lower = more factual, higher = more creative
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 500  # Max tokens to generate
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(OLLAMA_API, json=payload)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Connection error: {e}"
    
    def load_extracted_data(self, excel_file="staff_report.xlsx"):
        """Load the data we extracted"""
        if not os.path.exists(excel_file):
            print(f"❌ {excel_file} not found")
            return None
        
        df = pd.read_excel(excel_file)
        print(f"✅ Loaded {len(df)} records from {excel_file}")
        return df
    
    def generate_summary(self, data_df):
        """Generate executive summary using local LLM"""
        print(f"\n🤖 Generating summary with {self.model}...")
        
        # Convert data to readable format
        data_text = data_df.to_string(index=False)
        
        prompt = f"""
You are a healthcare operations analyst. Review this staff data:

{data_text}

Provide:
1. ONE sentence executive summary
2. Total number of staff
3. List of unique job titles found
4. Any missing or incomplete data

Keep response concise and professional.
"""
        
        response = self.generate(prompt, temperature=0.3)
        return response
    
    def detect_anomalies(self, data_df):
        """Find data quality issues"""
        data_text = data_df.to_string(index=False)
        
        prompt = f"""
Analyze this healthcare staff data for anomalies:

{data_text}

Look for:
- Missing employee IDs
- Incomplete or weird names
- Unusual job titles
- Formatting issues

List each issue. If none found, say "No anomalies detected."
"""
        
        response = self.generate(prompt, temperature=0.2)
        return response
    
    def generate_recommendations(self, data_df):
        """Get actionable recommendations"""
        data_text = data_df.to_string(index=False)
        
        prompt = f"""
Based on this staff data:

{data_text}

Suggest 3 actionable recommendations to improve data quality or staffing.
Keep each recommendation to one sentence.
"""
        
        response = self.generate(prompt, temperature=0.4)
        return response
    
    def create_html_report(self, data_df, summary, anomalies, recommendations):
        """Generate beautiful HTML report"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Healthcare Staff Report - AI Analysis</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            border-left: 4px solid #2a5298;
        }}
        .card h3 {{
            margin: 0 0 15px 0;
            color: #1e3c72;
        }}
        .anomaly-card {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        .recommendation-card {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #2a5298;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-success {{
            background: #28a745;
            color: white;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Healthcare Staff Intelligence Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>AI Model: {self.model} (Local Ollama)</p>
        </div>
        
        <div class="content">
            <div class="card">
                <h3>📊 Executive Summary</h3>
                <div style="white-space: pre-wrap;">{summary}</div>
            </div>
            
            <div class="card anomaly-card">
                <h3>⚠️ Data Quality Anomalies</h3>
                <div style="white-space: pre-wrap;">{anomalies}</div>
            </div>
            
            <div class="card recommendation-card">
                <h3>💡 Recommendations</h3>
                <div style="white-space: pre-wrap;">{recommendations}</div>
            </div>
            
            <h3>📋 Extracted Staff Data</h3>
            <div style="overflow-x: auto;">
                {data_df.to_html(index=False)}
            </div>
            
            <div class="footer">
                <p>🔒 Data processed locally via Ollama - No external API calls</p>
                <p>Automated by Playwright + Ollama AI Pipeline</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        with open("ollama_report.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Saved: ollama_report.html")
        
        # Also save text version
        with open("ollama_summary.txt", "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("HEALTHCARE STAFF REPORT (Ollama AI)\n")
            f.write("="*60 + "\n\n")
            f.write("SUMMARY:\n" + summary + "\n\n")
            f.write("ANOMALIES:\n" + anomalies + "\n\n")
            f.write("RECOMMENDATIONS:\n" + recommendations + "\n")
        print("✅ Saved: ollama_summary.txt")
    
    def run_pipeline(self, excel_file="staff_report.xlsx"):
        """Complete pipeline: load data + AI analysis"""
        print("\n" + "="*60)
        print("🤖 OLLAMA AI REPORTING PIPELINE")
        print("="*60)
        
        # Check Ollama
        if not self.check_ollama():
            print("\n💡 Start Ollama with: ollama serve")
            return
        
        # Load data
        df = self.load_extracted_data(excel_file)
        if df is None or len(df) == 0:
            print("❌ No data to analyze")
            return
        
        print(f"\n📊 Data preview:")
        print(df.head())
        
        # Generate AI insights
        summary = self.generate_summary(df)
        print("\n" + "="*40)
        print("📝 SUMMARY:")
        print("="*40)
        print(summary)
        
        anomalies = self.detect_anomalies(df)
        print("\n" + "="*40)
        print("⚠️ ANOMALIES:")
        print("="*40)
        print(anomalies)
        
        recommendations = self.generate_recommendations(df)
        print("\n" + "="*40)
        print("💡 RECOMMENDATIONS:")
        print("="*40)
        print(recommendations)
        
        # Create HTML report
        self.create_html_report(df, summary, anomalies, recommendations)
        
        print("\n" + "="*60)
        print("🎉 PIPELINE COMPLETE!")
        print("📄 Open ollama_report.html in your browser")
        print("="*60)

# ========== RUN ==========
if __name__ == "__main__":
    # Initialize with phi3 (fastest) or mistral (smarter)
    reporter = OllamaReporter(model="phi3")  # Change to "mistral" if you have it
    
    # Run the pipeline
    reporter.run_pipeline("staff_report.xlsx")