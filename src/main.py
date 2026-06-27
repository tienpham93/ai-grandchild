import os
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import FileResponse
from src.skills.anonymizer import scrub_pii
from src.agents.investigator import analyze_risk
from src.agents.companion import generate_companion_response
from src.agents.bridge import format_family_alert

# Check for API key at startup
if not os.environ.get("GEMINI_API_KEY"):
    print("❌ ERROR: GEMINI_API_KEY environment variable not set.")
    print("Please set it in your .env file or environment.")
    exit(1)

app = FastAPI(title="AI Grandchild - Zalo Webhook Server")

def process_zalo_event(json_payload: dict):
    """
    Runs the agent pipeline in the background so we don't block the 
    immediate 200 OK response to Zalo.
    """
    print("="*60)
    print(f"📥 RECEIVED EVENT: {json_payload.get('event_name', 'Unknown')}")
    
    # 1. Anonymize PII
    safe_payload = scrub_pii(json_payload)
    print(f"🛡️  [Anonymizer] Scrubbed Payload: {safe_payload}")
    
    # 2. Investigator Analysis
    print("\n🔍 [Investigator Agent] Analyzing...")
    try:
        risk_analysis = analyze_risk(safe_payload)
        print(f"   Risk Level: {risk_analysis.get('risk_level')}")
        print(f"   Reasoning: {risk_analysis.get('reasoning')}")
        
        # 3. Companion Response
        print("\n💬 [Companion Agent] Generating reply...")
        reply = generate_companion_response(
            context=str(safe_payload), 
            risk_level=risk_analysis.get('risk_level', 'UNKNOWN')
        )
        print(f"   Reply: {reply}")
        
        # 4. Bridge Alert (if needed)
        if risk_analysis.get('risk_level') == "HIGH":
            print("\n🚨 [Bridge Agent] Drafting family alert...")
            alert = format_family_alert(safe_payload, risk_analysis)
            print(f"   Alert: {alert}")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        
    print("="*60 + "\n")

@app.post("/webhook")
async def handle_zalo_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming webhook events from the Zalo Official Account.
    Returns 200 OK immediately and processes the event in the background.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}
        
    # Queue the heavy LLM processing in the background
    background_tasks.add_task(process_zalo_event, payload)
    
    # Immediately acknowledge receipt to Zalo
    return {"status": "success", "message": "Event received and queued for processing."}

@app.get("/")
def root():
    return {"status": "running", "message": "AI Grandchild Webhook Server is active."}

@app.get("/{filename}")
def serve_static_file(filename: str):
    """
    Serves static files from the /static directory.
    Used for Zalo domain verification HTML files.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "static", filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}, 404
