import os
import subprocess
import tempfile
import modal

# Define the app
app = modal.App("stockscrap-portfolio-sync")

# Image with system git and python dependencies
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install("feedparser", "beautifulsoup4", "requests", "python-dateutil", "GitPython", "PyGithub", "modal")
)

# Specialized image for LLM inference (with GPU support)
llm_image = (
    modal.Image.debian_slim()
    .pip_install("torch", "transformers", "accelerate", "huggingface-hub")
)

@app.function(
    image=llm_image,
    gpu="L4",
    timeout=600,
    container_idle_timeout=60,
)
def llm_inference(prompt: str):
    """
    Self-hosted Qwen-2.5-7B-Instruct inference on Modal GPU.
    """
    import torch
    from transformers import pipeline

    model_id = "Qwen/Qwen2.5-7B-Instruct"
    
    print(f"🤖 Loading {model_id} on GPU...")
    pipe = pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )

    messages = [
        {"role": "system", "content": "You are a senior financial analyst providing concise, data-driven analysis."},
        {"role": "user", "content": prompt},
    ]

    print("🖋️ Generating analysis...")
    outputs = pipe(
        messages,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    
    return outputs[0]["generated_text"][-1]["content"]

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("github-secret"),
        modal.Secret.from_name("googlecloud-secret")
    ],
    schedule=modal.Period(hours=24),
    timeout=1200
)
def sync_portfolio_news():
    import git
    import github
    
    repo_url = "https://github.com/enochwork123-stack/stockscrap.git"
    github_token = os.environ["GITHUB_TOKEN"]
    
    # Auth setup
    g = github.Github(auth=github.Auth.Token(github_token))
    user = g.get_user()
    print(f"👤 Authenticated as: {user.login}")

    with tempfile.TemporaryDirectory() as dname:
        # 1. Clone the repository
        auth_url = repo_url.replace("https://", f"https://{github_token}@")
        print(f"📂 Cloning repository to {dname}...")
        repo = git.Repo.clone_from(auth_url, dname)
        
        # 2. Add local path for imports
        import sys
        if dname not in sys.path:
            sys.path.append(dname)

        # 3. Run Step 0 Natively (with direct LLM handle for permissions)
        try:
            print("🔍 Step 0: Scraping Portfolio News Natively...")
            from tools.scrape_portfolio import run_scraping
            run_scraping(llm_inference_handle=llm_inference)
        except Exception as e:
            print(f"⚠️ Native Step 0 failed, falling back to rule-based in bash: {e}")

        # 4. Run the rest of the pipeline in the cloned directory
        print("📰 Running remaining news update pipeline...")
        try:
            env = os.environ.copy()
            env["SKIP_STEP_0"] = "1"
            subprocess.run(["bash", "update_dashboard.sh"], cwd=dname, check=True, text=True, env=env)
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
            return

        # 3. Check for changes in the dashboard payload
        payload_path = "data/dashboard_payload.js"
        abs_payload_path = os.path.join(dname, payload_path)

        if payload_path in [item.a_path for item in repo.index.diff(None)] or payload_path in repo.untracked_files:
            print("✨ New news articles found. Pushing via GitHub API...")

            # Use PyGithub REST API to update the file — avoids git push auth issues entirely.
            # The same token used here already works for cloning (confirmed by auth check above).
            gh_repo = g.get_repo("enochwork123-stack/stockscrap")
            with open(abs_payload_path, "rb") as f:
                new_content = f.read()

            try:
                # File exists — get its SHA and update it
                existing = gh_repo.get_contents(payload_path, ref="main")
                gh_repo.update_file(
                    path=payload_path,
                    message="Automated daily news update [Modal]",
                    content=new_content,
                    sha=existing.sha,
                    branch="main"
                )
            except Exception:
                # File doesn't exist yet — create it
                gh_repo.create_file(
                    path=payload_path,
                    message="Automated daily news update [Modal]",
                    content=new_content,
                    branch="main"
                )

            print("🚀 Successfully pushed updated dashboard to GitHub via API.")
        else:
            print("😴 No new news articles to update.")

@app.local_entrypoint()
def main():
    """Trigger the sync manually: modal run modal_app.py"""
    sync_portfolio_news.remote()
