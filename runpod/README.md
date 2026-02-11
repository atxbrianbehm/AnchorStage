# RunPod Serverless — Apple SHARP

Deploy Apple SHARP as a RunPod Serverless endpoint for fast, reliable 3DGS generation.

## Step 1: Build & Push Docker Image

You need Docker installed locally, or use RunPod's GitHub integration.

```bash
# From the runpod/ directory
docker build -t your-dockerhub-user/sharp-runpod:latest .
docker push your-dockerhub-user/sharp-runpod:latest
```

**Or use GitHub Container Registry:**
```bash
docker build -t ghcr.io/your-user/sharp-runpod:latest .
docker push ghcr.io/your-user/sharp-runpod:latest
```

## Step 2: Create RunPod Serverless Endpoint

1. Go to [runpod.io/console/serverless](https://www.runpod.io/console/serverless)
2. Click **New Endpoint**
3. Set:
   - **Container Image**: `your-dockerhub-user/sharp-runpod:latest`
   - **GPU**: A40 or A100 (16GB+ VRAM required, A40 is cheapest)
   - **Max Workers**: 1 (scale up if needed)
   - **Idle Timeout**: 5 seconds
   - **Execution Timeout**: 120 seconds
4. Click **Deploy**
5. Copy the **Endpoint ID** (e.g., `abc123def456`)

## Step 3: Get Your RunPod API Key

1. Go to [runpod.io/console/user/settings](https://www.runpod.io/console/user/settings)
2. Under **API Keys**, create a new key or copy existing
3. Save it — you'll need it for the backend

## Step 4: Configure AnchorStage Backend

Set these environment variables when running the server:

```powershell
$env:RUNPOD_API_KEY = "your-runpod-api-key"
$env:RUNPOD_ENDPOINT_ID = "your-endpoint-id"
python -m uvicorn web_demo:app --host 127.0.0.1 --port 8000
```

The backend will automatically use RunPod when these are set, falling back to HuggingFace Space if not.

## Expected Performance

| Step | Time |
|------|------|
| Cold start (first request) | ~30s (model loads from baked checkpoint) |
| Warm inference (512px) | ~5-10s |
| PLY transfer (base64 over API) | ~2-5s |
| **Total (warm)** | **~8-15s** |

Compare to HuggingFace free tier: 60-300s+ with frequent timeouts.

## Cost

- A40: ~$0.39/hr (only charged while processing)
- Idle workers cost nothing (scales to zero)
- Typical image: ~10s = ~$0.001 per image

## Testing the Endpoint

```bash
# Encode an image
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("test.jpg"))

# Call the endpoint
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" `
  -H "Authorization: Bearer YOUR_API_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"input\": {\"image_b64\": \"$b64\"}}"
```
