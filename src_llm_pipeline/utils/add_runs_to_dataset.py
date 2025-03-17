import json
from langsmith import Client
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import requests

def load_config():
    current_script_dir = Path(__file__).resolve().parent
    config_path = current_script_dir.parent / 'config.json'
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def add_runs_to_dataset():
    load_dotenv()
    
    config = load_config()

    client = Client()
    
    dataset_tag = config["dataset_tag"]
    delete_dataset = config["delete_dataset"]
    split = config["split"]
    share_dataset = config["share_dataset"]
    

    timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    dataset_name = f"{dataset_tag}_{timestamp}"
    
    print("Dataset name:", dataset_name)
    print("Dataset tag:", dataset_tag)
    
    # Filter runs to add to the dataset
    runs = list(client.list_runs(
        project_name="LLM-Classification-Pipeline",
        run_type="chain",
        is_root=True,
        filter=f'has(tags, "{dataset_tag}")',
        error=False,
    ))

    if not runs:
        print("No runs found matching the criteria.")
        return None

    if delete_dataset:
        if client.has_dataset(dataset_name=dataset_name):
            client.delete_dataset(dataset_name=dataset_name)
            print("Deleted existing dataset")
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Default Dataset for Langsmith Development runs last 14 days",
            inputs_schema={
                "type": "object",
                "title": "dataset_input_schema",
                "required": ["step_1_classification"],
                "properties": {
                    "step_1_classification": {"type": "object"},
                },
            },
            outputs_schema={
                "type": "object",
                "title": "dataset_output_schema",
                "required": ["step_2_classification_summary"],
                "properties": {
                    "step_2_classification_summary": {"type": "string"}
                }
            }
        )
        existing_run_ids = set()
    else:
        if client.has_dataset(dataset_name=dataset_name):
            dataset = client.read_dataset(dataset_name=dataset_name)
            print("Loaded existing dataset")
            # Fetch existing examples to avoid duplicates
            existing_examples = client.list_examples(dataset_id=dataset.id)
            existing_run_ids = {example.source_run_id for example in existing_examples if example.source_run_id}
        else:
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description="Default Dataset for Langsmith Development runs last 14 days",
                inputs_schema={
                    "type": "object",
                    "title": "dataset_input_schema",
                    "required": ["step_1_classification"],
                    "properties": {
                        "step_1_classification": {"type": "object"},
                    },
                },
                outputs_schema={
                    "type": "object",
                    "title": "dataset_output_schema",
                    "required": ["step_2_classification_summary"],
                    "properties": {
                        "step_2_classification_summary": {"type": "string"}
                    }
                }
            )
            print("Created new dataset")
            existing_run_ids = set()

    # Filter out runs that have already been added
    new_runs = [run for run in runs if run.id not in existing_run_ids]

    if not new_runs:
        print("All runs are already in the dataset.")
        # Try to read existing shared link
        try:
            share_info = client.read_dataset_shared_schema(dataset_id=dataset.id)
            print(f"Your dataset is already shared. Shareable link: {share_info['url']}")
        except Exception as e:
            print(f"Failed to retrieve existing share link: {e}")
        return share_info["url"] if 'share_info' in locals() else None

    # Add new runs to the dataset
    examples_to_add = []
    for run in new_runs:
        # Retrieve and use optional metadata from the run
        prompt_tokens = getattr(run, 'prompt_tokens', None)
        completion_tokens = getattr(run, 'completion_tokens', None)
        total_tokens = getattr(run, 'total_tokens', None)
        tags = getattr(run, 'tags', [])
        run_id = str(run.id)
        feedback = getattr(run, 'feedback_stats', {})
        print(run.feedback_stats)

        input_data = run.outputs.get("model-Step 1: Classification")
        output_data = run.outputs.get("model-Step 2: Summarization")

        if isinstance(input_data, str):
            input_data = json.loads(input_data)

        # Prepare metadata dictionary including additional data
        example_metadata = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "avg. coherence" : run.feedback_stats["coherence"]["avg"],
            "tags": tags,
            "run_id": run_id,
            "feedback": feedback,
            "user_id": tags[1] if len(tags) > 1 else None,
        }

        example = {
            "inputs": {"step_1_classification": input_data},
            "outputs": {"step_2_classification_summary": output_data},
            "metadata": {k: v for k, v in example_metadata.items() if v is not None}, # only include non-None metadata
            "created_at": run.end_time,
            "dataset_id": dataset.id,
            "split": split,
            "source_run_id": run.id,
        }
        examples_to_add.append(example)

    # Use bulk creation for efficiency
    client.create_examples(
        inputs=[ex["inputs"] for ex in examples_to_add],
        outputs=[ex["outputs"] for ex in examples_to_add],
        metadata=[ex["metadata"] for ex in examples_to_add],
        splits=[ex["split"] for ex in examples_to_add],
        source_run_ids=[ex["source_run_id"] for ex in examples_to_add],
        dataset_id=dataset.id,
    )

    # Try to share the dataset
    if share_dataset:
        try:
            share_info = client.share_dataset(dataset_id=dataset.id)
            print(f"Your dataset is now public. Shareable link: {share_info['url']}")
        except requests.exceptions.HTTPError as e:
            if "409 Client Error: Conflict" in str(e) and "already shared" in str(e):
                # Handle existing shared link
                share_info = client.read_dataset_shared_schema(dataset_id=dataset.id)
                print(f"Your dataset was already shared. Shareable link: {share_info['url']}")
            else:
                raise
        return share_info["url"]
    return "Not Shared - Change config to create sharable link"

    

if __name__ == '__main__':
    link = add_runs_to_dataset()
    if link:
        print(f"Dataset link: {link}")