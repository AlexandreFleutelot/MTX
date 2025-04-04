import google.generativeai as genai
import os
import time
from dotenv import load_dotenv 

def add_gemini_embeddings(page_data_dict, text_field='texte', embedding_field='embedding', model_name='models/embedding-001', task_type="RETRIEVAL_DOCUMENT"):

    # --- 1. Configure API Key ---
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # --- 2. Iterate through data and compute embeddings ---
    count = 0
    success_count = 0
    skipped_count = 0
    error_count = 0
    total_pages = len(page_data_dict)
    start_time = time.time()

    print(f"\nProcessing {total_pages} pages...")

    for page_url, page_data in page_data_dict.items():
        count += 1
        progress_prefix = f"({count}/{total_pages})"

        # Skip if embedding already computed (for resuming)
        if embedding_field in page_data and page_data[embedding_field] is not None:
            skipped_count += 1
            continue 

        # Get text content
        text_to_embed = page_data.get(text_field, ' ')

        # Validate text content
        if not text_to_embed or not isinstance(text_to_embed, str) or len(text_to_embed.strip()) == 0:
            print(f"{progress_prefix} Skipping {page_url[:70]}... (No valid text in '{text_field}')")
            page_data[embedding_field] = None # Mark as processed, no embedding possible
            skipped_count += 1
            continue

        # Compute embedding
        try:
            result = genai.embed_content(
                model=model_name,
                content=text_to_embed,
                task_type=task_type
            )

            embedding_vector = result.get('embedding')

            if embedding_vector and isinstance(embedding_vector, list):
                page_data[embedding_field] = embedding_vector
                success_count += 1
                if count % 100 == 0: # Log progress periodically
                     print(f"{progress_prefix} Processed.")
            else:
                print(f"{progress_prefix} Warning: API success for {page_url[:70]}... but no embedding vector found. Result: {result}")
                page_data[embedding_field] = None
                error_count += 1

            time.sleep(1.1) # 60 RPM limit

        except Exception as e:
            print(f"{progress_prefix} Error embedding {page_url[:70]}... Error: {e}")
            page_data[embedding_field] = None # Mark as failed
            error_count += 1
            # Optional: Implement more robust error handling/retry logic here
            time.sleep(2) # Wait a bit longer after an error

    # --- 3. Report Summary ---
    end_time = time.time()
    duration = end_time - start_time
    print("\n--- Embedding Process Finished ---")
    print(f"Total pages considered: {total_pages}")
    print(f"Successfully embedded: {success_count}")
    print(f"Skipped (no text or already done): {skipped_count}")
    print(f"Errors during embedding: {error_count}")
    print(f"Total time taken: {duration:.2f} seconds")

    return True # Indicate completion (even with errors)
