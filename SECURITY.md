# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of blog-creator-agent seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Reporting Process

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: wchoi189@gmail.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Security Update Process

1. **Report received**: Security team acknowledges receipt
2. **Investigation**: Team investigates and validates the vulnerability
3. **Fix development**: Patch is developed and tested
4. **Release**: Security update is released
5. **Disclosure**: Public disclosure after users have had time to update

## Security Best Practices for Deployment

### Environment Variables

Always set the following environment variables in production:

```bash
# Required - Generate a strong secret key
SECRET_KEY=<generate-strong-random-key>

# Required - Configure your API keys
OPENAI_API_KEY=<your-openai-key>
UPSTAGE_API_KEY=<your-upstage-key>

# Required - Production database URLs
REDIS_URL=redis://your-redis-host:6379/0
```

**Never use default values in production!**

### Generate a Secure SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use OpenSSL:
```bash
openssl rand -base64 32
```

### CORS Configuration

In production, restrict CORS origins to your actual domains:

```python
# backend/config.py
CORS_ORIGINS = ["https://yourdomain.com", "https://api.yourdomain.com"]
```

### File Upload Security

The application restricts uploads to specific file types:
- Documents: .pdf, .md
- Audio: .mp3, .wav, .m4a
- Images: .png, .jpg, .jpeg

Maximum file size: 50MB (configurable via `MAX_UPLOAD_SIZE`)

### Authentication

- JWT access tokens expire after 15 minutes
- Refresh tokens expire after 7 days
- Passwords are hashed using bcrypt with SHA-256 pre-hashing

### Dependencies

Keep dependencies up-to-date:

```bash
# Frontend
cd frontend && npm audit fix

# Backend
pip-audit
pip install --upgrade <package-name>
```

## Recent Security Updates

### 2025-11-26: Comprehensive Security Audit
- ✅ Resolved 21 Python dependency vulnerabilities
- ✅ Updated: certifi, configobj, cryptography, idna, jinja2, pip, requests, setuptools, twisted, urllib3
- ✅ Verified 0 vulnerabilities in frontend npm packages
- ✅ Comprehensive security best practices review completed
- See: [Audit Report](docs/audit/AUDIT_REPORT_2025-11-26.md)

## Security Features

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- bcrypt password hashing with SHA-256 pre-hashing
- Token type validation (prevents token misuse)
- User ownership verification on all operations

### Input Validation
- Pydantic models for all API requests/responses
- File type whitelist for uploads
- File size limits enforced
- UUID-based file paths (prevents path traversal)

### Infrastructure
- Redis for session management and caching
- Elasticsearch for document search
- NoSQL databases (no SQL injection risk)
- CORS protection

## Known Limitations

1. **Rate Limiting**: Not currently implemented. Consider adding for production.
2. **Security Headers**: Standard FastAPI headers. Consider adding additional security headers.
3. **Audit Logging**: Basic logging. Consider implementing security event tracking.

## Acknowledgments

We appreciate the security research community's efforts in responsibly disclosing vulnerabilities. Contributors who report valid security issues will be acknowledged (with their permission) in our release notes.

## Additional Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Security](https://nextjs.org/docs/advanced-features/security-headers)

---

**Last Updated**: 2025-11-26  
**Next Review**: 2026-01-26
