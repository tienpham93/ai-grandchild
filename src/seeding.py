# src/seeding.py
import os
import json
import asyncio

# Project Modules
from src.database import init_db, get_db, Family, Member
from src.pipeline import process_chat_event

async def run_simulation():
    print("--- AI Grandchild CLI Simulation & Seeding Started ---")
    
    # 1. Initialize SQLite Database Tables
    init_db()

    # 2. Use a generic ID for offline testing simulation
    test_chat_id = "123456789"

    # 3. Seed Database with a test Family/Member if not already present
    db_session = next(get_db())
    test_senior = db_session.query(Member).filter(Member.chat_id == test_chat_id).first()
    
    if not test_senior:
        print(f"💡 Seeding mock Senior user {test_chat_id} to SQLite database...")
        
        # Ensure a family exists
        fam = db_session.query(Family).first()
        if not fam:
            fam = Family(name="Gia đình Ngoại Bảy")
            db_session.add(fam)
            db_session.commit()
            db_session.refresh(fam)
        
        member = Member(
            chat_id=test_chat_id,
            family_id=fam.id,
            name="Ngoại Bảy",
            member_type="senior",
            member_role="grandpa"
        )
        db_session.add(member)
        db_session.commit()
    db_session.close()

    # 4. Load Mock Data Payloads
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mock_data_path = os.path.join(base_dir, "data", "mock_inputs.json")
    if not os.path.exists(mock_data_path):
        print(f"❌ Error: Mock data file not found at {mock_data_path}")
        return

    with open(mock_data_path, 'r', encoding='utf-8') as f:
        mock_inputs = json.load(f)

    # 5. Run the offline mock pipeline execution
    for i, mock_payload in enumerate(mock_inputs):
        print(f"\n--- Processing Mock Scenario {i+1} ---")
        await process_chat_event(mock_payload, chat_id=test_chat_id) 
    
    print("\n--- AI Grandchild CLI Simulation Finished ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())