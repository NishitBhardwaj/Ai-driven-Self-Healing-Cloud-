# Fake Identity Provider

This is a mock OAuth2/OIDC identity provider using MockServer.

## Endpoints

- `/.well-known/openid-configuration` - OpenID Connect discovery endpoint
- `/authorize` - Authorization endpoint
- `/token` - Token endpoint
- `/userinfo` - User info endpoint
- `/.well-known/jwks.json` - JSON Web Key Set

## Configuration

The MockServer configuration is defined in `mockserver-config.json`.

## Testing

```bash
# Get OpenID configuration
curl http://localhost:8082/.well-known/openid-configuration

# MockServer control API
curl http://localhost:8083/mockserver/status
```

