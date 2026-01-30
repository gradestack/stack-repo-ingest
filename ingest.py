#!/usr/bin/env python3
"""
GitHub repo ingestion - extracts complete engineering context
"""
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
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
            'pr_intelligence': self._mine_pr_comments(repo),
            'shadow_infrastructure': self._discover_shadow_infrastructure(repo),
            'commit_archaeology': self._analyze_commit_patterns(repo),
            'code_fear_indicators': self._detect_code_fear(repo),
            'hidden_dependencies': self._discover_hidden_dependencies(repo),
            'ci_analysis': self._analyze_ci_performance(repo),
            'ingested_at': datetime.now(timezone.utc).isoformat()
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

    def _mine_pr_comments(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Mine PR comments for confusion, tech debt, and fragility signals"""
        print("  Mining PR comments...")

        intelligence = {
            'confusion_signals': [],
            'tech_debt_acknowledgments': [],
            'fragility_mentions': [],
            'common_discussion_topics': [],
            'total_prs_analyzed': 0,
            'total_comments_analyzed': 0
        }

        try:
            # Get closed PRs (merged ones have actual implementation discussion)
            # Limit to recent 100 PRs to avoid rate limits
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            analyzed_count = 0
            for pr in pulls:
                if analyzed_count >= 100:  # Limit to avoid rate limit issues
                    break

                analyzed_count += 1

                try:
                    # Get all comments (review comments + issue comments)
                    comments = list(pr.get_issue_comments()) + list(pr.get_comments())
                    intelligence['total_comments_analyzed'] += len(comments)

                    for comment in comments:
                        body = comment.body.lower() if comment.body else ""

                        # Pattern 1: Confusion signals
                        confusion_patterns = [
                            'how does',
                            'why does',
                            'what is',
                            'what does',
                            'confused',
                            'unclear',
                            'not sure',
                            "don't understand",
                            'can you explain',
                            'what\'s the difference'
                        ]

                        for pattern in confusion_patterns:
                            if pattern in body:
                                intelligence['confusion_signals'].append({
                                    'pr': pr.number,
                                    'pr_title': pr.title,
                                    'pattern': pattern,
                                    'snippet': body[:200]  # First 200 chars
                                })
                                break

                        # Pattern 2: Tech debt acknowledgments
                        debt_patterns = [
                            'should probably',
                            'we should',
                            'todo',
                            'fixme',
                            'hack',
                            'workaround',
                            'technical debt',
                            'tech debt',
                            'will fix later',
                            'temporary',
                            'quick fix'
                        ]

                        for pattern in debt_patterns:
                            if pattern in body:
                                intelligence['tech_debt_acknowledgments'].append({
                                    'pr': pr.number,
                                    'pr_title': pr.title,
                                    'pattern': pattern,
                                    'snippet': body[:200]
                                })
                                break

                        # Pattern 3: Fragility mentions
                        fragility_patterns = [
                            'breaks',
                            'breaks when',
                            'fails',
                            'doesn\'t work',
                            'broken',
                            'regression',
                            'flaky',
                            'intermittent',
                            'sometimes fails',
                            'race condition'
                        ]

                        for pattern in fragility_patterns:
                            if pattern in body:
                                intelligence['fragility_mentions'].append({
                                    'pr': pr.number,
                                    'pr_title': pr.title,
                                    'pattern': pattern,
                                    'snippet': body[:200]
                                })
                                break

                except GithubException as e:
                    # Skip PRs that error (might be access issues)
                    continue

            intelligence['total_prs_analyzed'] = analyzed_count

            # Aggregate common topics
            all_signals = (
                intelligence['confusion_signals'] +
                intelligence['tech_debt_acknowledgments'] +
                intelligence['fragility_mentions']
            )

            # Count pattern frequencies
            pattern_counts = {}
            for signal in all_signals:
                pattern = signal['pattern']
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

            # Sort by frequency
            intelligence['common_discussion_topics'] = sorted(
                [{'pattern': k, 'count': v} for k, v in pattern_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]  # Top 10

            print(f"    Analyzed {analyzed_count} PRs, {intelligence['total_comments_analyzed']} comments")
            print(f"    Found {len(intelligence['confusion_signals'])} confusion signals")
            print(f"    Found {len(intelligence['tech_debt_acknowledgments'])} tech debt mentions")
            print(f"    Found {len(intelligence['fragility_mentions'])} fragility mentions")

        except GithubException as e:
            print(f"    Error mining PR comments: {e}")

        return intelligence

    def _discover_shadow_infrastructure(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Discover the ACTUAL workflows and tooling developers use"""
        print("  Discovering shadow infrastructure...")

        shadow = {
            'makefile_targets': self._parse_makefile(repo),
            'npm_scripts': self._parse_package_json_scripts(repo),
            'python_scripts': self._parse_pyproject_scripts(repo),
            'env_complexity': self._analyze_env_vars(repo),
            'workaround_scripts': self._find_workaround_scripts(repo),
            'docker_compose_stack': self._parse_docker_compose(repo),
            'insights': []
        }

        # Synthesize actionable insights
        shadow['insights'] = self._synthesize_shadow_insights(shadow)

        print(f"    Found {len(shadow['insights'])} shadow infrastructure insights")

        return shadow

    def _parse_makefile(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Parse Makefile to understand actual workflows"""
        try:
            makefile = repo.get_contents("Makefile")
            content = makefile.decoded_content.decode('utf-8')

            targets = []
            current_target = None
            commands = {}

            for line in content.split('\n'):
                # Target line (starts at column 0, ends with :)
                if line and not line.startswith('\t') and ':' in line and not line.startswith('#'):
                    target = line.split(':')[0].strip()
                    if target and not target.startswith('.'):
                        targets.append(target)
                        current_target = target
                        commands[target] = []
                # Command line (starts with tab)
                elif line.startswith('\t') and current_target:
                    cmd = line.strip()
                    if cmd and not cmd.startswith('@echo') and not cmd.startswith('#'):
                        commands[current_target].append(cmd.lstrip('@'))

            # Analyze patterns
            has_deploy = any('deploy' in t for t in targets)
            has_test = any('test' in t for t in targets)
            has_docker = any('docker' in str(commands) for t in targets)

            return {
                'exists': True,
                'targets': targets,
                'commands': commands,
                'has_deploy_target': has_deploy,
                'has_test_target': has_test,
                'uses_docker': has_docker,
                'total_targets': len(targets)
            }

        except GithubException:
            return {'exists': False}

    def _parse_package_json_scripts(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Parse package.json scripts to understand Node.js workflows"""
        try:
            pkg = repo.get_contents("package.json")
            content = json.loads(pkg.decoded_content.decode('utf-8'))

            scripts = content.get('scripts', {})

            # Detect patterns
            has_fast_test = 'test:fast' in scripts or 'test:quick' in scripts
            has_debug = any('debug' in s for s in scripts.keys())
            has_docker = any('docker' in s for s in scripts.keys())
            has_deploy = any('deploy' in s for s in scripts.keys())
            has_postinstall = 'postinstall' in scripts

            # Count test variants
            test_scripts = [s for s in scripts.keys() if 'test' in s]

            return {
                'exists': True,
                'scripts': scripts,
                'has_fast_test': has_fast_test,
                'has_debug_mode': has_debug,
                'has_docker_scripts': has_docker,
                'has_deploy_scripts': has_deploy,
                'postinstall_hook': has_postinstall,
                'test_script_count': len(test_scripts),
                'total_scripts': len(scripts)
            }

        except (GithubException, json.JSONDecodeError):
            return {'exists': False}

    def _parse_pyproject_scripts(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Parse pyproject.toml for Python project scripts"""
        try:
            import re
            pyproject = repo.get_contents("pyproject.toml")
            content = pyproject.decoded_content.decode('utf-8')

            # Look for [tool.uv.scripts] or [project.scripts]
            scripts = {}
            in_scripts_section = False

            for line in content.split('\n'):
                if '[tool.uv.scripts]' in line or '[project.scripts]' in line:
                    in_scripts_section = True
                    continue
                elif line.startswith('[') and in_scripts_section:
                    in_scripts_section = False
                elif in_scripts_section and '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"\'')
                        scripts[key] = value

            return {
                'exists': True,
                'scripts': scripts,
                'total_scripts': len(scripts)
            }

        except GithubException:
            return {'exists': False}

    def _analyze_env_vars(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Analyze .env.example to understand configuration complexity"""
        try:
            env_file = repo.get_contents(".env.example")
            content = env_file.decoded_content.decode('utf-8')

            lines = content.split('\n')
            vars = []
            red_flags = []

            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var_name = line.split('=')[0].strip()
                    vars.append(var_name)

                    # Check for red flags
                    if any(flag in var_name.lower() for flag in ['magic', 'dont_change', 'do_not', 'legacy', 'hack', 'temp']):
                        red_flags.append(var_name)

            # Categorize
            categories = {
                'database': len([v for v in vars if any(db in v.lower() for db in ['database', 'db_', 'postgres', 'mysql', 'mongo'])]),
                'cache': len([v for v in vars if any(c in v.lower() for c in ['redis', 'cache', 'memcache'])]),
                'cloud': len([v for v in vars if any(c in v.lower() for c in ['aws', 'gcp', 'azure', 's3', 'bucket'])]),
                'auth': len([v for v in vars if any(a in v.lower() for a in ['auth', 'secret', 'key', 'token'])]),
                'observability': len([v for v in vars if any(o in v.lower() for o in ['sentry', 'datadog', 'newrelic', 'log'])]),
                'feature_flags': len([v for v in vars if any(f in v.lower() for f in ['enable', 'feature', 'flag'])]),
            }

            complexity = 'low' if len(vars) < 5 else 'medium' if len(vars) < 15 else 'high'

            return {
                'exists': True,
                'total_vars': len(vars),
                'variables': vars,
                'categories': categories,
                'red_flags': red_flags,
                'complexity': complexity
            }

        except GithubException:
            return {'exists': False}

    def _find_workaround_scripts(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Find shell scripts that indicate workarounds"""
        try:
            workarounds = []
            standard_paths = ['scripts/', 'bin/', '.git/', '.github/']

            # Get all files in root
            contents = repo.get_contents("")

            for item in contents:
                if item.type == "file" and item.name.endswith('.sh'):
                    # Scripts in root are usually workarounds
                    if not any(item.path.startswith(p) for p in standard_paths):
                        workarounds.append({
                            'name': item.name,
                            'path': item.path,
                            'location': 'root'
                        })

            # Check scripts/ directory for suspicious names
            try:
                scripts_dir = repo.get_contents("scripts")
                if isinstance(scripts_dir, list):
                    for item in scripts_dir:
                        if item.name.endswith('.sh'):
                            name_lower = item.name.lower()
                            if any(keyword in name_lower for keyword in ['fix', 'manual', 'restart', 'workaround', 'temp', 'hack']):
                                workarounds.append({
                                    'name': item.name,
                                    'path': item.path,
                                    'location': 'scripts',
                                    'suspicious_name': True
                                })
            except GithubException:
                pass

            return {
                'found': len(workarounds) > 0,
                'count': len(workarounds),
                'scripts': workarounds
            }

        except GithubException:
            return {'found': False, 'count': 0}

    def _parse_docker_compose(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Parse docker-compose files to understand local dev requirements"""
        try:
            # Try multiple possible names
            compose_files = [
                'docker-compose.yml',
                'docker-compose.yaml',
                'docker-compose.local.yml',
                'docker-compose.dev.yml'
            ]

            services = []
            volumes = []

            for filename in compose_files:
                try:
                    compose_file = repo.get_contents(filename)
                    content = compose_file.decoded_content.decode('utf-8')

                    # Basic YAML parsing (look for service names)
                    in_services = False
                    for line in content.split('\n'):
                        if line.strip() == 'services:':
                            in_services = True
                            continue
                        elif line.strip().startswith('volumes:') or line.strip().startswith('networks:'):
                            in_services = False
                        elif in_services and line and not line.startswith(' ' * 4) and ':' in line:
                            service_name = line.split(':')[0].strip()
                            if service_name and service_name not in services:
                                services.append(service_name)

                except GithubException:
                    continue

            # Analyze services
            has_db = any(db in str(services).lower() for db in ['postgres', 'mysql', 'mongo', 'mariadb'])
            has_cache = any(cache in str(services).lower() for cache in ['redis', 'memcache'])
            has_queue = any(q in str(services).lower() for q in ['rabbitmq', 'kafka', 'celery'])

            complexity = 'low' if len(services) <= 2 else 'medium' if len(services) <= 4 else 'high'

            return {
                'exists': len(services) > 0,
                'services': services,
                'service_count': len(services),
                'has_database': has_db,
                'has_cache': has_cache,
                'has_queue': has_queue,
                'complexity': complexity
            }

        except GithubException:
            return {'exists': False}

    def _synthesize_shadow_insights(self, shadow: Dict[str, Any]) -> List[Dict[str, str]]:
        """Synthesize actionable insights from shadow infrastructure data"""
        insights = []

        # Insight 1: Manual deployment detected
        if shadow['makefile_targets'].get('has_deploy_target'):
            insights.append({
                'category': 'deployment',
                'issue': 'manual_deployment_detected',
                'severity': 'medium',
                'description': 'Makefile contains deploy target, suggesting manual deployments',
                'suggestion': 'Consider automated deployments with proper rollback mechanisms'
            })

        # Insight 2: Test performance issues
        if shadow['npm_scripts'].get('has_fast_test'):
            insights.append({
                'category': 'testing',
                'issue': 'slow_tests',
                'severity': 'medium',
                'description': 'Fast test variant exists, indicating regular tests are too slow',
                'suggestion': 'Optimize test suite or implement test parallelization in CI'
            })

        # Insight 3: Dependency patching (tech debt)
        if shadow['npm_scripts'].get('postinstall_hook'):
            insights.append({
                'category': 'dependencies',
                'issue': 'postinstall_patches',
                'severity': 'high',
                'description': 'postinstall hook detected, likely patching dependencies',
                'suggestion': 'Investigate dependency issues and consider alternatives'
            })

        # Insight 4: High configuration complexity
        if shadow['env_complexity'].get('complexity') == 'high':
            insights.append({
                'category': 'configuration',
                'issue': 'high_config_complexity',
                'severity': 'medium',
                'description': f"{shadow['env_complexity'].get('total_vars', 0)} environment variables required",
                'suggestion': 'Consider secrets manager or configuration service to reduce onboarding friction'
            })

        # Insight 5: Configuration red flags
        if shadow['env_complexity'].get('red_flags'):
            insights.append({
                'category': 'configuration',
                'issue': 'config_red_flags',
                'severity': 'high',
                'description': f"Suspicious env vars: {', '.join(shadow['env_complexity']['red_flags'])}",
                'suggestion': 'Document these variables or refactor to remove magic values'
            })

        # Insight 6: Workaround scripts
        if shadow['workaround_scripts'].get('count', 0) > 0:
            insights.append({
                'category': 'process',
                'issue': 'workaround_scripts_found',
                'severity': 'medium',
                'description': f"{shadow['workaround_scripts']['count']} workaround scripts detected",
                'suggestion': 'These scripts indicate manual processes that should be automated'
            })

        # Insight 7: Complex local dev setup
        if shadow['docker_compose_stack'].get('service_count', 0) > 3:
            insights.append({
                'category': 'developer_experience',
                'issue': 'complex_local_dev',
                'severity': 'medium',
                'description': f"{shadow['docker_compose_stack']['service_count']} services required for local development",
                'suggestion': 'High onboarding friction - consider dev environment improvements or remote dev options'
            })

        return insights

    def _analyze_commit_patterns(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Analyze git commit patterns to understand team behavior"""
        print("  Analyzing commit patterns...")

        patterns = {
            'total_commits': 0,
            'commit_times': {'weekday': {}, 'hour': {}},
            'revert_commits': [],
            'friday_deploys': 0,
            'weekend_activity': 0,
            'avg_commit_message_length': 0,
            'insights': []
        }

        try:
            # Get recent commits (limit to 200 to avoid rate limits)
            commits = list(repo.get_commits()[:200])
            patterns['total_commits'] = len(commits)

            if len(commits) == 0:
                return patterns

            commit_message_lengths = []

            for commit in commits:
                # Time patterns
                commit_time = commit.commit.author.date
                weekday = commit_time.strftime('%A')
                hour = commit_time.hour

                patterns['commit_times']['weekday'][weekday] = \
                    patterns['commit_times']['weekday'].get(weekday, 0) + 1
                patterns['commit_times']['hour'][str(hour)] = \
                    patterns['commit_times']['hour'].get(str(hour), 0) + 1

                # Friday deploys
                if weekday == 'Friday':
                    patterns['friday_deploys'] += 1

                # Weekend activity
                if weekday in ['Saturday', 'Sunday']:
                    patterns['weekend_activity'] += 1

                # Revert detection
                message = commit.commit.message.lower()
                if any(keyword in message for keyword in ['revert', 'rollback', 'roll back']):
                    patterns['revert_commits'].append({
                        'sha': commit.sha[:7],
                        'message': commit.commit.message.split('\n')[0][:100],
                        'date': commit_time.isoformat()
                    })

                commit_message_lengths.append(len(commit.commit.message))

            # Calculate averages
            if commit_message_lengths:
                patterns['avg_commit_message_length'] = \
                    sum(commit_message_lengths) / len(commit_message_lengths)

            # Generate insights
            revert_rate = len(patterns['revert_commits']) / len(commits) if commits else 0
            friday_ratio = patterns['friday_deploys'] / len(commits) if commits else 0
            weekend_ratio = patterns['weekend_activity'] / len(commits) if commits else 0

            if revert_rate > 0.03:  # More than 3% reverts
                patterns['insights'].append({
                    'category': 'stability',
                    'issue': 'high_revert_rate',
                    'severity': 'high',
                    'description': f'{len(patterns["revert_commits"])} reverts in {len(commits)} commits ({revert_rate*100:.1f}%)',
                    'suggestion': 'High revert rate suggests deployment or testing issues'
                })

            if friday_ratio < 0.05:  # Less than 5% Friday commits
                patterns['insights'].append({
                    'category': 'culture',
                    'issue': 'friday_deploy_avoidance',
                    'severity': 'medium',
                    'description': 'Very few Friday commits, suggesting deploy fear',
                    'suggestion': 'Build confidence with better testing and rollback procedures'
                })

            if weekend_ratio > 0.15:  # More than 15% weekend work
                patterns['insights'].append({
                    'category': 'culture',
                    'issue': 'weekend_work',
                    'severity': 'medium',
                    'description': f'{weekend_ratio*100:.1f}% of commits on weekends',
                    'suggestion': 'High weekend activity may indicate incident response or work-life balance issues'
                })

            if patterns['avg_commit_message_length'] < 20:
                patterns['insights'].append({
                    'category': 'process',
                    'issue': 'poor_commit_messages',
                    'severity': 'low',
                    'description': f'Average commit message length: {patterns["avg_commit_message_length"]:.0f} chars',
                    'suggestion': 'Short commit messages make code archaeology difficult'
                })

            print(f"    Analyzed {len(commits)} commits, found {len(patterns['insights'])} insights")

        except GithubException as e:
            print(f"    Error analyzing commits: {e}")

        return patterns

    def _detect_code_fear(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Detect code fear indicators - areas developers are afraid to touch"""
        print("  Detecting code fear indicators...")

        fear = {
            'sacred_cows': [],
            'frozen_files': [],
            'defensive_code_files': [],
            'total_fear_signals': 0,
            'insights': []
        }

        try:
            # Search for fear patterns in code
            fear_keywords = [
                'DO NOT TOUCH',
                'DO NOT CHANGE',
                "DON'T TOUCH",
                "DON'T CHANGE",
                'FRAGILE',
                'DANGEROUS',
                'CAREFUL',
                'XXX',
                'HACK HACK',
                'WARNING WARNING'
            ]

            for keyword in fear_keywords:
                try:
                    # GitHub code search
                    query = f'{keyword} repo:{repo.full_name}'
                    results = self.github.search_code(query)

                    for result in list(results)[:10]:  # Limit to 10 results per keyword
                        fear['sacred_cows'].append({
                            'file': result.path,
                            'keyword': keyword,
                            'url': result.html_url
                        })
                except GithubException:
                    # Search API might be rate limited or unavailable
                    continue

            fear['total_fear_signals'] = len(fear['sacred_cows'])

            # Generate insights
            if fear['total_fear_signals'] > 5:
                fear['insights'].append({
                    'category': 'code_quality',
                    'issue': 'high_fear_signals',
                    'severity': 'high',
                    'description': f'{fear["total_fear_signals"]} fear keywords found in code',
                    'suggestion': 'Multiple "DO NOT TOUCH" warnings suggest technical debt and low confidence'
                })

            print(f"    Found {fear['total_fear_signals']} fear signals")

        except Exception as e:
            print(f"    Error detecting code fear: {e}")

        return fear

    def _discover_hidden_dependencies(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Discover hidden dependencies not in package managers"""
        print("  Discovering hidden dependencies...")

        hidden = {
            'system_dependencies': [],
            'runtime_fetches': [],
            'external_apis': [],
            'total_hidden_deps': 0,
            'insights': []
        }

        try:
            # Parse Dockerfile for system dependencies
            try:
                dockerfile = repo.get_contents("Dockerfile")
                content = dockerfile.decoded_content.decode('utf-8')

                for line in content.split('\n'):
                    line = line.strip()
                    if 'apt-get install' in line or 'apk add' in line or 'yum install' in line:
                        # Extract package names
                        packages = line.split('install')[1] if 'install' in line else ''
                        packages = packages.replace('\\', '').replace('-y', '').replace('--no-cache', '').strip()
                        if packages and not packages.startswith('#'):
                            hidden['system_dependencies'].append({
                                'source': 'Dockerfile',
                                'packages': packages[:200]  # Limit length
                            })

            except GithubException:
                pass

            # Check for curl/wget in shell scripts (runtime fetches)
            try:
                contents = repo.get_contents("")
                for item in contents:
                    if item.type == "file" and item.name.endswith('.sh'):
                        try:
                            script_content = item.decoded_content.decode('utf-8')
                            if 'curl ' in script_content or 'wget ' in script_content:
                                hidden['runtime_fetches'].append({
                                    'file': item.path,
                                    'type': 'shell_script'
                                })
                        except:
                            continue
            except GithubException:
                pass

            hidden['total_hidden_deps'] = \
                len(hidden['system_dependencies']) + \
                len(hidden['runtime_fetches'])

            # Generate insights
            if hidden['system_dependencies']:
                hidden['insights'].append({
                    'category': 'dependencies',
                    'issue': 'system_dependencies_required',
                    'severity': 'medium',
                    'description': f'{len(hidden["system_dependencies"])} system dependency declarations found',
                    'suggestion': 'System dependencies increase deployment complexity'
                })

            if hidden['runtime_fetches']:
                hidden['insights'].append({
                    'category': 'dependencies',
                    'issue': 'runtime_fetches_detected',
                    'severity': 'medium',
                    'description': f'{len(hidden["runtime_fetches"])} scripts with runtime fetches (curl/wget)',
                    'suggestion': 'Runtime fetches can fail and are hard to version'
                })

            print(f"    Found {hidden['total_hidden_deps']} hidden dependencies")

        except Exception as e:
            print(f"    Error discovering hidden dependencies: {e}")

        return hidden

    def _analyze_ci_performance(self, repo: Repository.Repository) -> Dict[str, Any]:
        """Analyze CI/CD performance and identify bottlenecks"""
        print("  Analyzing CI/CD performance...")

        ci_analysis = {
            'workflow_count': 0,
            'workflows': [],
            'recent_runs': [],
            'insights': []
        }

        try:
            # Get GitHub Actions workflows
            try:
                workflows = repo.get_workflows()
                ci_analysis['workflow_count'] = workflows.totalCount

                for workflow in list(workflows)[:5]:  # Limit to 5 workflows
                    workflow_data = {
                        'name': workflow.name,
                        'path': workflow.path,
                        'state': workflow.state
                    }

                    # Get recent runs for this workflow
                    try:
                        runs = list(workflow.get_runs()[:10])  # Last 10 runs

                        if runs:
                            # Calculate average duration
                            durations = []
                            failures = 0

                            for run in runs:
                                if run.conclusion == 'failure':
                                    failures += 1

                                # Calculate duration if both times exist
                                if run.created_at and run.updated_at:
                                    duration = (run.updated_at - run.created_at).total_seconds()
                                    durations.append(duration)

                            if durations:
                                avg_duration = sum(durations) / len(durations)
                                workflow_data['avg_duration_seconds'] = int(avg_duration)
                                workflow_data['avg_duration_minutes'] = round(avg_duration / 60, 1)

                            workflow_data['failure_rate'] = failures / len(runs) if runs else 0
                            workflow_data['recent_runs'] = len(runs)

                    except GithubException:
                        pass

                    ci_analysis['workflows'].append(workflow_data)

            except GithubException:
                pass

            # Generate insights
            for workflow in ci_analysis['workflows']:
                if workflow.get('avg_duration_minutes', 0) > 15:
                    ci_analysis['insights'].append({
                        'category': 'ci_performance',
                        'issue': 'slow_ci_workflow',
                        'severity': 'medium',
                        'description': f'{workflow["name"]}: {workflow["avg_duration_minutes"]} minute average runtime',
                        'suggestion': 'Consider caching, parallelization, or splitting workflows'
                    })

                if workflow.get('failure_rate', 0) > 0.2:
                    ci_analysis['insights'].append({
                        'category': 'ci_reliability',
                        'issue': 'flaky_ci_workflow',
                        'severity': 'high',
                        'description': f'{workflow["name"]}: {workflow["failure_rate"]*100:.0f}% failure rate',
                        'suggestion': 'High failure rate suggests flaky tests or environment issues'
                    })

            print(f"    Analyzed {len(ci_analysis['workflows'])} workflows, found {len(ci_analysis['insights'])} insights")

        except Exception as e:
            print(f"    Error analyzing CI/CD: {e}")

        return ci_analysis

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
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'repos': [r['metadata']['name'] for r in results]
    }

    with open('output/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Ingested {len(results)} repos")
    print(f"✓ Output saved to: output/")


if __name__ == '__main__':
    main()
