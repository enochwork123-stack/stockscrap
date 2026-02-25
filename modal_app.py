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
    .pip_install("feedparser", "beautifulsoup4", "requests", "python-dateutil", "GitPython", "PyGithub", "google-generativeai")
)

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
        
        # 2. Run the update pipeline in the cloned directory
        print("📰 Running portfolio news update pipeline...")
        try:
            # We use the existing scripts in the repo
            subprocess.run(["bash", "update_dashboard.sh"], cwd=dname, check=True, text=True)
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
