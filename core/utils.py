from typing import Optional

def build_http_proxy(proxy_cfg: Optional[Any]) -> Optional[str]:
    """Builds a proxy URL for httpx."""
    if not proxy_cfg:
        return None
    
    # Basic implementation for socks/http
    # Note: httpx requires 'httpx[socks]' for socks support
    protocol = "socks5" if proxy_cfg.type == "socks5" else "http"
    proxy_url = f"{protocol}://{proxy_cfg.server}:{proxy_cfg.port}"
    if proxy_cfg.secret:
        proxy_url += f"@{proxy_cfg.secret}"
    return proxy_url
