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
    .pip_install("feedparser", "beautifulsoup4", "requests", "python-dateutil", "GitPython", "PyGithub")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("github-secret")],
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
        if payload_path in [item.a_path for item in repo.index.diff(None)] or payload_path in repo.untracked_files:
            print("✨ New news articles found. Committing changes...")
            
            # Configure git user
            repo.config_writer().set_value("user", "name", "Glaid bot").release()
            repo.config_writer().set_value("user", "email", "bot@glaid.ai").release()
            
            # Commit and Push
            repo.index.add([payload_path])
            repo.index.commit("Automated daily news update [Modal]")
            origin = repo.remote(name='origin')
            # Explicitly set the authenticated URL on the remote before pushing.
            # clone_from may strip the token from the origin URL, causing a 403.
            origin.set_url(auth_url)
            origin.push()
            print("🚀 Successfully pushed updated dashboard to GitHub.")
        else:
            print("😴 No new news articles to update.")

@app.local_entrypoint()
def main():
    """Trigger the sync manually: modal run modal_app.py"""
    sync_portfolio_news.remote()
