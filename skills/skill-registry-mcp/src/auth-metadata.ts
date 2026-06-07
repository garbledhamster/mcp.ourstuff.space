export interface AuthMetadataEnv {
  SKILL_REGISTRY_MCP_PUBLIC_READ?: string;
  SKILL_REGISTRY_OAUTH_ISSUER?: string;
  SKILL_REGISTRY_OAUTH_AUTHORIZATION_ENDPOINT?: string;
  SKILL_REGISTRY_OAUTH_TOKEN_ENDPOINT?: string;
  SKILL_REGISTRY_OAUTH_REGISTRATION_ENDPOINT?: string;
}

export function protectedResourceMetadata(request: Request, env: AuthMetadataEnv) {
  const origin = new URL(request.url).origin;
  const issuer = env.SKILL_REGISTRY_OAUTH_ISSUER?.replace(/\/+$/, "");
  return {
    resource: `${origin}/mcp`,
    authorization_servers: issuer ? [issuer] : [],
    bearer_methods_supported: ["header"],
    scopes_supported: ["skills.read"],
    resource_documentation: `${origin}/health`,
    mcp_auth_status: authStatus(Boolean(issuer), publicReadEnabled(env))
  };
}

export function authorizationServerMetadata(request: Request, env: AuthMetadataEnv) {
  const origin = new URL(request.url).origin;
  const issuer = env.SKILL_REGISTRY_OAUTH_ISSUER?.replace(/\/+$/, "") || origin;
  const oauthConfigured = Boolean(
    env.SKILL_REGISTRY_OAUTH_ISSUER &&
      env.SKILL_REGISTRY_OAUTH_AUTHORIZATION_ENDPOINT &&
      env.SKILL_REGISTRY_OAUTH_TOKEN_ENDPOINT
  );

  return {
    issuer,
    authorization_endpoint: env.SKILL_REGISTRY_OAUTH_AUTHORIZATION_ENDPOINT || null,
    token_endpoint: env.SKILL_REGISTRY_OAUTH_TOKEN_ENDPOINT || null,
    registration_endpoint: env.SKILL_REGISTRY_OAUTH_REGISTRATION_ENDPOINT || null,
    response_types_supported: oauthConfigured ? ["code"] : [],
    grant_types_supported: oauthConfigured ? ["authorization_code", "refresh_token"] : [],
    token_endpoint_auth_methods_supported: oauthConfigured ? ["client_secret_basic", "none"] : [],
    code_challenge_methods_supported: oauthConfigured ? ["S256"] : [],
    scopes_supported: ["skills.read"],
    mcp_auth_status: authStatus(oauthConfigured, publicReadEnabled(env))
  };
}

export function mcpAuthChallenge(request: Request): string {
  const origin = new URL(request.url).origin;
  return `Bearer realm="skill-registry-mcp", resource_metadata="${origin}/.well-known/oauth-protected-resource"`;
}

export function publicReadEnabled(env: Pick<AuthMetadataEnv, "SKILL_REGISTRY_MCP_PUBLIC_READ">): boolean {
  return env.SKILL_REGISTRY_MCP_PUBLIC_READ === "true";
}

function authStatus(oauthConfigured: boolean, publicRead: boolean) {
  return {
    oauth_implemented: oauthConfigured,
    public_read_enabled: publicRead,
    private_bearer_token_supported: true,
    local_stdio_adapter_supported: true,
    cloudflare_access_supported_for_mcp: false,
    identity_verification: publicRead
      ? "No-auth mode does not verify ChatGPT user email, account, or workspace identity. It only exposes approved read-only MCP content publicly."
      : "Identity verification requires OAuth or another verifiable signed-token flow.",
    note: publicRead
      ? "v1 public read mode is enabled for /mcp: approved skills are public; admin and pending review remain private."
      : oauthConfigured
      ? "OAuth discovery metadata is configured. Token verification must still be validated against the target MCP client."
      : "v1 supports private bearer-token mode and local stdio adapter mode, not full remote OAuth login yet.",
    distinctions: {
      tls_success: "HTTPS certificate and path are reachable.",
      bearer_token_success: "Private SKILL_REGISTRY_READ_TOKEN or SKILL_REGISTRY_ADMIN_TOKEN was accepted.",
      mcp_auth_success: "The target MCP client completed MCP-compatible auth discovery/login and then connected."
    }
  };
}
