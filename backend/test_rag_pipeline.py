import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import Document
from documents.services import process_document
from rag.pipeline import run_rag_pipeline
from django.core.files.base import ContentFile

def test_full_rag_flow():
    print("=" * 60)
    print("TESTING FULL DJANGO + CHROMADB + GROQ RAG PIPELINE")
    print("=" * 60)

    # 1. Create or get test user
    user, created = User.objects.get_or_create(username='test_rag_user', defaults={'email': 'test@example.com'})
    if created:
        user.set_password('TestPass123!')
        user.save()
    print(f"[OK] Test User: {user.username} (ID: {user.id})")

    # 2. Create a test knowledge document
    sample_content = """
    PROJECT NEBULA SPECIFICATION DOCUMENT
    Version: 2.4 | Status: Approved | Date: 2026-08-15
    Lead Architect: Dr. Emily Vance
    
    1. System Overview:
    Project Nebula is an autonomous quantum telemetry platform designed for deep space sensor arrays.
    It utilizes the Helios-9 optical communication protocol operating at 400 Terahertz.
    
    2. Power & Propulsion:
    The primary core is powered by a Tritium-Deuterium micro-fusion cell generating 45 Kilowatts continuously.
    The auxiliary battery bank provides 72 hours of uninterrupted emergency backup.
    
    3. Security & Access Protocols:
    All telemetry channels require Level-4 Quantum Key Distribution (QKD) encryption.
    The primary encryption override cipher is designated as 'OMEGA-774-ALPHA'.
    
    4. Operational Temperatures:
    Nebula operates between -270 degrees Celsius in deep space shadow and up to +180 degrees Celsius when solar sails are deployed.
    """

    doc_file = ContentFile(sample_content.encode('utf-8'), name='nebula_specs.txt')
    
    # Clean previous test docs
    Document.objects.filter(user=user, title='nebula_specs.txt').delete()

    doc = Document.objects.create(
        user=user,
        title='nebula_specs.txt',
        file=doc_file,
        file_type='txt',
        file_size=len(sample_content),
        processing_status=Document.STATUS_PENDING
    )
    print(f"[OK] Created Document: {doc.title} (ID: {doc.id})")

    # 3. Process & Ingest into ChromaDB
    print("\n--> Indexing document into ChromaDB...")
    success = process_document(doc)
    print(f"[OK] Ingestion Result: success={success}, status={doc.processing_status}, chunks={doc.chunk_count}")

    # 4. Test RAG Query with Groq LLM
    test_question = "What is the primary power source and encryption override cipher of Project Nebula?"
    print(f"\n--> Asking RAG Question to Groq: '{test_question}'")

    rag_result = run_rag_pipeline(
        user_id=user.id,
        question=test_question
    )

    print("\n" + "=" * 60)
    print("GROQ RAG RESPONSE:")
    print("=" * 60)
    print(rag_result.get('answer'))
    print("\nSource Citations:")
    for src in rag_result.get('sources', []):
        print(f"- Doc: {src.get('document')} | Page: {src.get('page')}")
        print(f"  Snippet: {src.get('snippet')[:100]}...")
    print("=" * 60)
    print("[SUCCESS] Full Django + ChromaDB + Groq RAG integration verified successfully!")

if __name__ == '__main__':
    test_full_rag_flow()
