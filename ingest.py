#!/usr/bin/env python3
"""
GitHub repo ingestion - extracts complete engineering context
"""
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, Repository, GithubException
from dotenv import load_dotenv

load_dotenv()


# Files that define the stack - prioritized by importance
CRITICAL_FILES = {
    # Dependencies
    'package.json': 'nodejs_deps',
    'package-lock.json': 'nodejs_lock',
    'requirements.txt': 'python_deps',
    'Pipfile': 'python_pipfile',
    'pyproject.toml': 'python_project',
    'go.mod': 'go_deps',
    'go.sum': 'go_lock',
    'Gemfile': 'ruby_deps',
    'Cargo.toml': 'rust_deps',
    'pom.xml': 'java_maven',
    'build.gradle': 'java_gradle',
    'composer.json': 'php_deps',

    # Infrastructure
    'Dockerfile': 'docker',
    'docker-compose.yml': 'docker_compose',
    'docker-compose.yaml': 'docker_compose',
    'kubernetes.yml': 'k8s',
    'kubernetes.yaml': 'k8s',

    # IaC
    'terraform.tfvars': 'terraform_vars',
    'main.tf': 'terraform_main',
    'variables.tf': 'terraform_vars_def',

    # CI/CD
    '.github/workflows': 'github_actions',
    '.gitlab-ci.yml': 'gitlab_ci',
    'Jenkinsfile': 'jenkins',
    '.circleci/config.yml': 'circleci',

    # Cloud/Platform
    'Procfile': 'heroku',
    'app.json': 'heroku_config',
    'vercel.json': 'vercel',
    'netlify.toml': 'netlify',

    # Docs
    'README.md': 'readme',
    'CONTRIBUTING.md': 'contributing',
}


class RepoIngester:
    """Ingests GitHub repositories and extracts engineering context"""

    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)

    def ingest_org(self, org_name: str) -> List[Dict[str, Any]]:
        """Ingest all repos from a GitHub organization"""
        print(f"Fetching repos from org: {org_name}")

        try:
            org = self.github.get_organization(org_name)
            repos = list(org.get_repos())
            print(f"Found {len(repos)} repositories")

            results = []
            for repo in repos:
                print(f"\nProcessing: {repo.name}")
                repo_data = self.ingest_repo(repo)
                results.append(repo_data)

                # Save individual repo output
                self._save_repo_output(repo.name, repo_data)

            return results

        except GithubException as e:
            print(f"Error fetching org: {e}")
            return []

    def ingest_repo(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Extract complete context from a single repo"""

        repo_data = {
            'metadata': self._get_repo_metadata(repo),
            'files': self._get_critical_files(repo),
            'structure': self._analyze_structure(repo),
            'ingested_at': datetime.utcnow().isoformat()
        }

        return repo_data

    def _get_repo_metadata(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Extract repo metadata"""
        return {
            'name': repo.name,
            'full_name': repo.full_name,
            'description': repo.description,
            'url': repo.html_url,
            'language': repo.language,
            'languages': self._get_languages(repo),
            'size_kb': repo.size,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'open_issues': repo.open_issues_count,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
            'default_branch': repo.default_branch,
            'archived': repo.archived,
            'topics': repo.get_topics() if hasattr(repo, 'get_topics') else [],
        }

    def _get_languages(self, repo: Repository.Repository) -> Dict[str, int]:
        """Get language breakdown"""
        try:
            return repo.get_languages()
        except:
            return {}

    def _get_critical_files(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Fetch contents of critical files that define the stack"""
        files = {}

        try:
            # Get root directory contents
            contents = repo.get_contents("")

            for file_pattern, file_type in CRITICAL_FILES.items():
                file_data = self._fetch_file_content(repo, file_pattern)
                if file_data:
                    files[file_type] = file_data

            # Special handling for workflow directories
            workflows = self._fetch_workflows(repo)
            if workflows:
                files['github_actions'] = workflows

            # Get all terraform files
            tf_files = self._fetch_terraform_files(repo)
            if tf_files:
                files['terraform_all'] = tf_files

            # Get kubernetes manifests
            k8s_files = self._fetch_k8s_files(repo)
            if k8s_files:
                files['k8s_all'] = k8s_files

        except GithubException as e:
            print(f"  Error fetching files: {e}")

        return files

    def _fetch_file_content(self, repo: Repository.Repository, path: str) -> Optional[Dict[str, str]]:
        """Fetch content of a specific file"""
        try:
            content = repo.get_contents(path)
            if content and not isinstance(content, list):
                decoded = content.decoded_content.decode('utf-8')
                return {
                    'path': path,
                    'content': decoded,
                    'size': content.size
                }
        except GithubException:
            pass
        return None

    def _fetch_workflows(self, repo: Repository.Repository) -> List[Dict[str, str]]:
        """Fetch all GitHub Actions workflows"""
        workflows = []
        try:
            contents = repo.get_contents(".github/workflows")
            if isinstance(contents, list):
                for item in contents:
                    if item.name.endswith(('.yml', '.yaml')):
                        decoded = item.decoded_content.decode('utf-8')
                        workflows.append({
                            'name': item.name,
                            'path': item.path,
                            'content': decoded
                        })
        except GithubException:
            pass
        return workflows

    def _fetch_terraform_files(self, repo: Repository.Repository) -> List[Dict[str, str]]:
        """Fetch all terraform files"""
        tf_files = []
        try:
            contents = repo.get_contents("")
            for item in contents:
                if isinstance(item, list):
                    continue
                if item.name.endswith('.tf'):
                    decoded = item.decoded_content.decode('utf-8')
                    tf_files.append({
                        'name': item.name,
                        'path': item.path,
                        'content': decoded
                    })
        except GithubException:
            pass
        return tf_files

    def _fetch_k8s_files(self, repo: Repository.Repository) -> List[Dict[str, str]]:
        """Fetch kubernetes manifests"""
        k8s_files = []
        k8s_dirs = ['k8s', 'kubernetes', 'manifests', 'deploy']

        for dirname in k8s_dirs:
            try:
                contents = repo.get_contents(dirname)
                if isinstance(contents, list):
                    for item in contents:
                        if item.name.endswith(('.yml', '.yaml')):
                            decoded = item.decoded_content.decode('utf-8')
                            k8s_files.append({
                                'name': item.name,
                                'path': item.path,
                                'content': decoded
                            })
            except GithubException:
                continue

        return k8s_files

    def _analyze_structure(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Analyze repo structure to understand architecture"""
        structure = {
            'has_tests': False,
            'has_docs': False,
            'has_ci': False,
            'has_docker': False,
            'has_iac': False,
            'directories': []
        }

        try:
            contents = repo.get_contents("")

            for item in contents:
                if item.type == "dir":
                    structure['directories'].append(item.name)

                    # Detect patterns
                    if item.name in ['test', 'tests', '__tests__', 'spec']:
                        structure['has_tests'] = True
                    if item.name in ['docs', 'documentation']:
                        structure['has_docs'] = True
                    if item.name in ['.github', '.gitlab', '.circleci']:
                        structure['has_ci'] = True
                    if item.name in ['terraform', 'k8s', 'kubernetes']:
                        structure['has_iac'] = True

                if item.type == "file":
                    if item.name == 'Dockerfile':
                        structure['has_docker'] = True

        except GithubException:
            pass

        return structure

    def _save_repo_output(self, repo_name: str, data: Dict[str, Any]):
        """Save repo data to JSON file"""
        filename = self.output_dir / f"{repo_name}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  Saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Ingest GitHub repos for stack context')
    parser.add_argument('--org', required=True, help='GitHub organization name')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')

    args = parser.parse_args()

    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token required. Set GITHUB_TOKEN env var or use --token")
        return

    ingester = RepoIngester(token)
    results = ingester.ingest_org(args.org)

    # Save summary
    summary = {
        'org': args.org,
        'repos_ingested': len(results),
        'timestamp': datetime.utcnow().isoformat(),
        'repos': [r['metadata']['name'] for r in results]
    }

    with open('output/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Ingested {len(results)} repos")
    print(f"✓ Output saved to: output/")


if __name__ == '__main__':
    main()
