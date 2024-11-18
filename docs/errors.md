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