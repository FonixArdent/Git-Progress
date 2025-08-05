import time
import re
import base64
from github import Github
from github.GithubException import GithubException
from boxes import show_box  # Custom error/info display

class Master:
    """
    Master class for managing and updating the progression status of a GitHub repository's README.
    """
    def __init__(self, data: tuple):
        USER: str = data[0]
        REPO: str = data[2]
        STATUS: str = data[3]
        VISIBILITY: str = data[4]

        TYPE = {"🌐 Public": "public", "🔒 Private": "private"}

        self.TOKEN: str = data[1]
        self.GitUser = USER
        self.GitData = (REPO, STATUS, TYPE.get(VISIBILITY, "public"))
        self.GitHub = Github(login_or_token=self.TOKEN)

    def GitCheck(self) -> bool:
        try:
            repo = self.GitHub.get_repo(f"{self.GitUser}/{self.GitData[0]}")
<<<<<<< HEAD
           # print(f"✅ Repository found: {repo.full_name}") >> test
=======
            # print(f"✅ Repository found: {repo.full_name}")
>>>>>>> 6dacb9028e0ff6cec8d446fdfbb8e322b80bbb75
            return True
        except GithubException as e:
            show_box(e.status if e.status in (404, 403) else 505, e)
            return False
        except Exception as e:
            show_box(101, e)
            return False

    def GitEdit(self):
        if not self.GitCheck():
            show_box(0, f"\n\n>> {__name__} : GitCheck Failed\n\n💠 Please try again.")
            return

        try:
            repo = self.GitHub.get_repo(f"{self.GitUser}/{self.GitData[0]}")
            is_private = repo.private
            expected_visibility = self.GitData[2]

            #.. Check repository visibility
            if expected_visibility == "public" and is_private:
                show_box(403, f"❌ The repository '{self.GitData[0]}' is private, but you selected 'Public'.")
                return

            if expected_visibility == "private" and not is_private:
                show_box(403, f"❌ The repository '{self.GitData[0]}' is public, but you selected 'Private'.")
                return

            show_box(20, f"✍️ Preparing to update the {expected_visibility} repository '{self.GitData[0]}'...")

            readme_file = repo.get_readme()
            content_decoded = base64.b64decode(readme_file.content).decode("utf-8")

            progress_map = {
                "under_dev": "🔴 Under Development",
                "ready_soon": "🟠 Soon Ready",
                "finished": "🟢 Ended",
                "under_update": "🔘 Updating",
            }
            progress_value = progress_map.get(self.GitData[1], "📛 Unknown")

            #.. Update the progression line in the README
            pattern = re.compile(r'^([ >\<\-\*\`]*progress\s*:\s*)(.*?)([ >\<\-\*\`]*)$', re.IGNORECASE | re.MULTILINE)

            def replace_progression(match):
                prefix = match.group(1)
                suffix = match.group(3)
                return f"{prefix}{progress_value}{suffix}\n"

            if re.search(pattern, content_decoded):
                updated_content = re.sub(pattern, replace_progression, content_decoded)
            else:
                #.. Add the progression line if it does not exist
                updated_content = content_decoded + f"\n\nProgress : {progress_value}"

            repo.update_file(
                path=readme_file.path,
                message=f"📝 Progression updated: {progress_value}",
                content=updated_content,
                sha=readme_file.sha
            )

            show_box(20, f"✅ Progression updated to '{progress_value}' in '{self.GitData[0]}'")
            time.sleep(1.5)

        except GithubException as e:
            show_box(e.status if e.status in (403, 404) else 505, e)
        except Exception as e:
            show_box(101, e)
