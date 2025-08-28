# Genie Backend Python - Enhanced Configuration Design

## Overview

The Genie Backend Python configuration has been significantly enhanced to support:
- **GitHub Integration**: Complete GitHub API integration for code analysis, repository management, and automated workflows
- **Multi-LLM Support**: Support for OpenAI, Claude, and Gemini with intelligent provider selection
- **Dynamic Agent Configuration**: Flexible agent configuration that adapts to task types and user preferences

## Configuration Structure

### 1. GitHub Integration Configuration

The agent now supports comprehensive GitHub integration capabilities:

```yaml
github:
  enabled: true
  access_token: '${GITHUB_ACCESS_TOKEN:your-github-access-token-here}'
  api_base_url: 'https://api.github.com'
  timeout: 30
  max_retries: 3
  repositories:
    default_org: 'your-organization'
    allowed_repos:
      - 'repo1'
      - 'repo2'
      - 'genie-backend-python'
```

#### GitHub Features:
- **Repository Analysis**: Analyze code structure, dependencies, and architecture
- **Pull Request Management**: Create, review, and manage pull requests
- **Issue Tracking**: Create and manage GitHub issues
- **Code Search**: Search across repositories and codebases
- **Commit History**: Analyze commit history and code changes
- **Webhook Integration**: Receive real-time notifications from GitHub

#### GitHub Permissions:
```yaml
github_integration:
  permissions:
    read_repos: true
    write_repos: false  # Set to true for repository modifications
    create_issues: true
    create_pull_requests: true
```

### 2. Multi-LLM Configuration

The system supports multiple LLM providers with intelligent selection:

```yaml
llm:
  default_provider: 'openai'  # Options: openai, claude, gemini
  
  providers:
    openai:
      enabled: true
      api_key: '${OPENAI_API_KEY:your-openai-api-key-here}'
      models:
        default: 'gpt-4-turbo-preview'
        available: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo']
      
    claude:
      enabled: true
      api_key: '${CLAUDE_API_KEY:your-claude-api-key-here}'
      models:
        default: 'claude-3-sonnet-20240229'
        available: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
      
    gemini:
      enabled: true
      api_key: '${GEMINI_API_KEY:your-gemini-api-key-here}'
      models:
        default: 'gemini-pro'
        available: ['gemini-pro', 'gemini-pro-vision']
```

#### LLM Selection Strategy:
```yaml
selection:
  strategy: 'user_preference'  # Options: user_preference, round_robin, load_based, task_based
  fallback_order: ['openai', 'claude', 'gemini']
  task_mapping:
    code_generation: 'openai'
    code_review: 'claude'
    planning: 'claude'
    search: 'gemini'
    default: 'openai'
```

### 3. Enhanced Agent Configuration

The agent system has been upgraded with GitHub and multi-LLM support:

#### Planning Agent:
- **GitHub-Aware Planning**: Incorporates GitHub operations into task planning
- **LLM Recommendations**: Suggests optimal LLM for each task type
- **Intelligent Task Breakdown**: Considers code complexity and repository structure

#### Executor Agent:
- **Multi-LLM Execution**: Can switch between LLMs during task execution
- **GitHub Integration**: Direct integration with GitHub APIs
- **Fallback Mechanisms**: Automatic fallback to alternative LLMs

#### React Agent:
- **GitHub Data Processing**: Incorporates GitHub data into responses
- **Cross-LLM Analysis**: Combines insights from multiple LLMs

### 4. Enhanced Tools Configuration

New and enhanced tools support the extended capabilities:

#### GitHub Tool:
```yaml
github_tool:
  desc: "GitHub集成工具，支持仓库分析、PR创建、Issue管理等功能"
  params:
    action: ["analyze_repo", "create_pr", "create_issue", "search_code", "get_commits"]
    repository: "owner/repo format"
    data: "Operation-specific data"
```

#### LLM Selector Tool:
```yaml
llm_selector:
  desc: "LLM选择工具，根据任务类型动态选择最适合的LLM提供商"
  params:
    task_type: ["code_generation", "code_review", "planning", "search", "analysis", "general"]
    preferred_provider: ["openai", "claude", "gemini", "auto"]
    fallback_enabled: true
```

#### Enhanced Planning Tool:
```yaml
plan_tool:
  desc: "增强的计划工具，支持GitHub集成和LLM选择推荐"
  params:
    llm_provider: "Recommended LLM for the task"
    github_action: "Required GitHub operations"
```

## Environment Variables

The system supports the following environment variables for secure configuration:

### Required Environment Variables:
- `GITHUB_ACCESS_TOKEN`: GitHub personal access token with appropriate permissions
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `GEMINI_API_KEY`: Google Gemini API key

### Optional Environment Variables:
- `GITHUB_WEBHOOK_SECRET`: Secret for GitHub webhook validation
- `OPENAI_BASE_URL`: Custom OpenAI API endpoint
- `CLAUDE_BASE_URL`: Custom Claude API endpoint
- `GEMINI_BASE_URL`: Custom Gemini API endpoint

## Configuration Examples

### Example 1: Code Review Workflow
```yaml
task_type: "code_review"
llm_provider: "claude"  # Best for code analysis
github_action: "analyze_repo"
permissions:
  read_repos: true
  create_issues: true
```

### Example 2: Feature Development
```yaml
task_type: "code_generation"
llm_provider: "openai"  # Best for code generation
github_action: "create_pr"
permissions:
  read_repos: true
  write_repos: true
  create_pull_requests: true
```

### Example 3: Research and Analysis
```yaml
task_type: "search"
llm_provider: "gemini"  # Best for information retrieval
github_action: "search_code"
permissions:
  read_repos: true
```

## Security Considerations

### GitHub Access:
- Use fine-grained personal access tokens
- Limit repository access to necessary repos only
- Enable webhook secret validation
- Regular token rotation

### LLM API Keys:
- Store API keys in environment variables
- Use separate keys for different environments
- Monitor API usage and costs
- Implement rate limiting

### Agent Permissions:
- Configure minimal required permissions
- Separate read and write access
- Audit agent actions regularly
- Implement approval workflows for sensitive operations

## Usage Patterns

### 1. Automatic LLM Selection:
The system automatically selects the best LLM based on task type:
- **Code Generation**: OpenAI GPT-4 (strong code generation capabilities)
- **Code Review**: Claude (excellent analysis and reasoning)
- **Planning**: Claude (superior planning and breakdown)
- **Search**: Gemini (efficient information retrieval)

### 2. GitHub Integration Workflows:
- **Repository Analysis**: Analyze codebase structure and suggest improvements
- **Automated PR Creation**: Generate code and create pull requests
- **Issue Management**: Track and manage development tasks
- **Code Search**: Find relevant code across repositories

### 3. Multi-Agent Collaboration:
- **Planning Agent**: Uses Claude for complex task breakdown
- **Executor Agent**: Switches between LLMs based on subtask requirements
- **GitHub Agent**: Handles all repository operations
- **Reporting Agent**: Combines insights from multiple sources

## Monitoring and Analytics

### LLM Usage Tracking:
```yaml
llm_analytics:
  enabled: true
  track_usage: true
  track_performance: true
  export_metrics: true
```

### GitHub Activity Monitoring:
- Track API usage and rate limits
- Monitor repository access patterns
- Log all GitHub operations
- Generate usage reports

## Migration Guide

### From Basic Configuration:
1. Add GitHub access token to environment variables
2. Configure LLM API keys for desired providers
3. Update agent prompts to include GitHub and multi-LLM context
4. Test GitHub permissions and LLM connectivity
5. Configure monitoring and analytics

### Best Practices:
- Start with read-only GitHub permissions
- Test LLM fallback mechanisms
- Monitor API usage and costs
- Implement gradual rollout for new features
- Regular security audits and token rotation

## Troubleshooting

### Common Issues:
1. **GitHub API Rate Limits**: Implement proper rate limiting and retry logic
2. **LLM API Failures**: Ensure fallback mechanisms are working
3. **Permission Errors**: Verify GitHub token permissions
4. **Configuration Errors**: Validate YAML syntax and environment variables

### Debug Mode:
Enable debug logging for detailed troubleshooting:
```yaml
logging:
  level:
    com.jd.genie: DEBUG
```

This enhanced configuration provides a robust foundation for building advanced AI agents with GitHub integration and multi-LLM support, enabling sophisticated code analysis, automated development workflows, and intelligent task execution.