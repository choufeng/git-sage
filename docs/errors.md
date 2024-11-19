# Git Sage Error Messages

This document catalogs various error messages you might encounter while using Git Sage, along with their causes and solutions.

## Model Related Errors

### Failed to Process Diff Due to Missing Model

**Error Message:**

```
Error: Failed to process diff: Failed to call language model
```

**Cause:**
This error occurs when Git Sage attempts to use an Ollama model that hasn't been downloaded to your local system yet.

**Solution:**

1. Ensure Ollama is installed on your system
2. Download the required model using the Ollama CLI:
   ```bash
   ollama pull <model-name>
   ```
3. Try your Git Sage command again

Note: Replace `<model-name>` with the specific model you're trying to use (e.g., llama2, codellama, etc.).

### Failed to Process Diff Due to Connection Error

**Error Message:**

```
Error: Failed to process diff: Failed to call language model: Connection error
```

**Cause:**
This error occurs when Git Sage cannot establish a connection with the language model service, typically due to network issues or service unavailability.

**Solution:**

1. Check your internet connection
2. Ensure the language model service is running
3. Try your Git Sage command again

### Failed to Process Diff Due to Token Limit Exceeded

**Error Message:**

```
Error: Failed to process diff: Failed to call language model: Error code: 400 - {'error': {'message': "This model's maximum context length is 65536 tokens. However, you requested 176915 tokens (176915 in the messages, 0 in the completion). Please reduce the length of the messages or completion.", 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_request_error'}}
```

**Cause:**
This error occurs when the code changes in your commit are too large and exceed the language model's maximum token limit (65536 tokens).

**Solution:**

1. Try breaking down your large commit into multiple smaller commits
2. Only include the most critical files in your commit
3. If using the `git-sage commit` command, use the `--files` parameter to specify which files to include to reduce the content being processed
