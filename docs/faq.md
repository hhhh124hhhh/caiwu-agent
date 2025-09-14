# FAQ

This page addresses frequently asked questions and common issues.

### Why is the agent's output truncated?

If you observe that the agent's output is being cut off unexpectedly, the issue may be related to the `max_output_token` limit set by the LLM service you are using.

For example, the DeepSeek [API](https://api-docs.deepseek.com/quick_start/pricing) sets a default limit of 4,096 output tokens for the `deepseek-chat` model, but this can be manually extended up to 8,192 tokens.

To resolve this, you can explicitly set the `max_tokens` parameter in your model's configuration (`ModelSettingsConfig`).

```yaml
model:
  # ... other provider settings
  model_settings:
    temperature: 0.3
    top_p: 0.95
    max_tokens: 8000
```

> For more context, see [this issue](https://github.com/TencentCloudADP/youtu-agent/issues/59).

### How can I resolve LLM request timeouts?

If you are encountering request timeouts, first ensure that the LLM service is operational. If the service is running correctly, you may need to increase the request timeout period.

The default timeout for the `openai` Python package is 600 seconds. You can override this by setting the `timeout` value within `extra_args` in your `ModelSettingsConfig`.

```yaml
model:
  # ... other provider settings
  model_settings:
    extra_args:
      timeout: 1200 # Sets the timeout to 1200 seconds
```
