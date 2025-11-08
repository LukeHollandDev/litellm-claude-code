# Claude Claude with LiteLLM

This repository contains a simple setup to use Claude Code with LiteLLM to take advantage of local models but using the
power of Claude Code and its agentic workflow.

_Local LLMs will not work as well as the official Anthropic models, but still a fun exercise._

This setup also illustrates the usage of the `apiKeyHelper` of Claude Code to issue the LiteLLM API key automatically
without needing to configure it. Additionally, LiteLLM is also configured to emit tracing to a local OpenTelemetry
collector.

[My OpenTelemetry stack for testing](https://github.com/LukeHollandDev/claude-code-otel)

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

There is a `.claude/settings.json` file which pre-configures these, additionally it configures an `apiKeyHelper` which
automatically supplies the API key for LiteLLM. This will automatically use the variables if running Claude in this
directory.

LiteLLM can be configured to use the `litellm/custom_auth.py` the code can be uncommented in the `litellm/config.yml`
and in the `docker-compose.yml`. (this is just experimental to test the behaviour of the feature)
