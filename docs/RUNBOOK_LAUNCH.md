# 🚀 OmniFy Launch Runbook

This runbook provides a concise checklist to deploy and verify OmniFy in production with Low-Cost Mode enabled.

## 1) Preflight
- Domains to point to ingress: `api.yourdomain.com`, `app.yourdomain.com`
- TLS issuer ready (cert-manager `letsencrypt` ClusterIssuer)
- GitHub Actions secrets added (if using CI deploy): `KUBE_CONFIG_PROD`
- Container registry (GHCR) access verified

## 2) Secrets
- Copy and edit `k8s/secrets.example.yaml` → `k8s/secrets.yaml`
- Required:
  - `MONGO_URL`
  - `JWT_SECRET_KEY`
- Optional: `OPENAI_API_KEY`, `AGENTKIT_API_KEY`, `GOHIGHLEVEL_*`, `LINKEDIN_*`, `SHOPIFY_*`, `STRIPE_*`
- Apply:
```bash
kubectl apply -f k8s/secrets.yaml
```

## 3) Images
- Build & push via CI or locally:
```bash
# API
docker build -t ghcr.io/<owner>/<repo>-api:latest -f backend/Dockerfile .
docker push ghcr.io/<owner>/<repo>-api:latest

# Frontend
docker build -t ghcr.io/<owner>/<repo>-frontend:latest -f frontend/Dockerfile .
docker push ghcr.io/<owner>/<repo>-frontend:latest
```

## 4) Deploy (Helm preferred)
```bash
helm upgrade --install omnify helm/ \
  --set image.api=ghcr.io/<owner>/<repo>-api:latest \
  --set image.frontend=ghcr.io/<owner>/<repo>-frontend:latest \
  --set ingress.hosts.api=api.yourdomain.com \
  --set ingress.hosts.app=app.yourdomain.com
```

Alternatively, apply manifests:
```bash
kubectl apply -f k8s/
```

## 5) Verify
```bash
# Pods ready
kubectl get pods

# API health
curl -s https://api.yourdomain.com/health | jq

# Cost usage (when LOW_COST_MODE=true)
curl -s https://api.yourdomain.com/api/cost/usage -H "X-Organization-Id: default" | jq
```
Expected: status healthy; quotas present in headers and body when LOW_COST_MODE=true.

## 6) Low-Cost Mode Settings
- In `.env` or k8s env:
  - `LOW_COST_MODE=true`
  - `RATE_LIMIT_RPM`, `QUOTA_REQUESTS_PER_DAY`, `QUOTA_TOKENS_PER_DAY`
  - `LLM_MAX_TOKENS`, `LLM_TOKEN_COST_PER_1K_USD`
- Quota headers returned on all responses.
- Cache headers (`Cache-Control`) on GET responses.

## 7) Monitoring & Logs
- Start with `kubectl logs -f deploy/omnify-api` for errors.
- Add Grafana/Prometheus stack when needed (see DEPLOYMENT_GUIDE).
- Set cloud alerts on domain uptime and latency.

## 8) Rollback
```bash
# Helm
helm rollback omnify <revision>

# Or redeploy previous image tag
helm upgrade --install omnify helm/ \
  --set image.api=ghcr.io/<owner>/<repo>-api:<prev> \
  --set image.frontend=ghcr.io/<owner>/<repo>-frontend:<prev>
```

## 9) Post-Launch SLOs (initial targets)
- API uptime ≥ 99.5%
- p95 latency ≤ 500ms for cached GETs, ≤ 1200ms for POSTs
- Error rate ≤ 1%
- Monthly cost cap as configured; 50/80/100% alerts

## 10) Go-Live Checklist
- [ ] Secrets applied
- [ ] Images pushed and references updated
- [ ] Helm install successful
- [ ] TLS valid and green lock visible
- [ ] `/health` returns healthy
- [ ] `/api/cost/usage` returns quotas
- [ ] Frontend loads, login works
- [ ] EYES module loads data and UI
- [ ] Basic platform action succeeds (e.g., GoHighLevel contact create)

You are live. Keep LOW_COST_MODE on for early-stage control; relax quotas as usage grows.
