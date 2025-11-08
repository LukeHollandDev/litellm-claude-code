# Claude Claude with LiteLLM

This repository contains a simple setup to use Claude Code with LiteLLM to take advantage of local models but using the
power of Claude Code and its agentic workflow.

_Local LLMs will not work as well as the official Anthropic models, but still a fun exercise._

This setup also illustrates the usage of the `apiKeyHelper` of Claude Code to issue a custom API key for authentication
with the local LLM provider and LiteLLM is configured to support OpenTelemetry for emitting events.

## Usage

### LiteLLM

Start the LiteLLM and PostgreSQL database stack:

```shell
docker compose up -d
```

### Claude Code Configuration

Set the following variables to configure Claude Code to use LiteLLM:

```shell
export ANTHROPIC_BASE_URL=http://localhost:4000
# configured in LiteLLM config
export ANTHROPIC_MODEL=qwen3-coder-30b
export ANTHROPIC_DEFAULT_HAIKU_MODEL=qwen3-coder-30b
export ANTHROPIC_DEFAULT_SONNET_MODEL=qwen3-coder-30b
```

There is also additional configuration for Claude Code which enables a custom API key to be sent, this is configured in
the `.claude` directory in this repository. There's a simple shell script which echos an API key which when configured,
Claude Code sends this with the LLM API requests.

LiteLLM can be configured to use the `litellm/custom_auth.py` the code can be uncommented in the `litellm/config.yml`
and in the `docker-compose.yml`.
