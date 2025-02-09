# Security Policy

## Supported Versions

Currently, we support the following versions of Tumblr Auto Like Bot with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Tumblr Auto Like Bot seriously. If you believe you have found a security vulnerability, please follow these steps:

1. **DO NOT** disclose the vulnerability publicly
2. Send a detailed report to [info@thrasher.fun] including:
   -  A description of the vulnerability
   -  Steps to reproduce the issue
   -  Potential impact
   -  Suggested fix (if any)

### What to expect

-  We will acknowledge receipt of your report within 48 hours
-  We will provide a detailed response within 7 days
-  We will keep you informed about the progress towards fixing the vulnerability
-  After the fix is released, we will publicly acknowledge your responsible disclosure (if you wish)

## Security Best Practices

When using Tumblr Auto Like Bot, please follow these security guidelines:

1. **API Credentials**

   -  Keep your Tumblr API credentials secure
   -  Never share your `.env` file
   -  Regularly rotate your API keys
   -  Use environment variables for sensitive data

2. **Rate Limiting**

   -  Respect Tumblr's API rate limits
   -  Keep daily and hourly limits at reasonable levels
   -  Monitor your API usage

3. **Access Control**

   -  Keep your bot's access token secure
   -  Regularly review authorized applications
   -  Revoke access immediately if compromised

4. **Updates**
   -  Keep the bot and its dependencies up to date
   -  Check for security advisories regularly
   -  Subscribe to security notifications

## Known Security Risks

1. **API Key Exposure**

   -  Risk: Accidentally committing API keys to public repositories
   -  Mitigation: Use `.env` files and `.gitignore`

2. **Rate Limit Abuse**

   -  Risk: Exceeding API limits, leading to account restrictions
   -  Mitigation: Implement proper rate limiting

3. **Dependency Vulnerabilities**
   -  Risk: Security issues in dependencies
   -  Mitigation: Regular updates and vulnerability scanning

## Security-Related Configuration

The bot includes several security-related configuration options:

```yaml
security:
   max_daily_likes: 1000
   max_hourly_likes: 100
   request_timeout: 30
   retry_limit: 3
```

## Secure Development

When contributing to the project:

1. Never commit sensitive data
2. Use secure coding practices
3. Validate all inputs
4. Handle errors securely
5. Follow the principle of least privilege

## Contact

For security-related inquiries, contact:

-  Email: [info@thrasher.fun]
-  PGP Public Key:

   ```
   -----BEGIN PGP PUBLIC KEY BLOCK-----
   Comment: User ID:	thrasher <info@thrasher.fun>
   Comment: Valid from:	10.02.2025 02:19
   Comment: Valid until:	10.02.2028 12:00
   Comment: Type:	255-bit EdDSA (secret key available)
   Comment: Usage:	Signing, Encryption, Certifying User IDs
   Comment: Fingerprint:	1830FB3E64668EC02B7CC0EA406AD51624CDA1C4
   ```

mDMEZ6k4GBYJKwYBBAHaRw8BAQdA8jV4OEaMzjjJa/6iclCut6LpHy6x7PxtCjxr
ouVfEAm0HHRocmFzaGVyIDxpbmZvQHRocmFzaGVyLmZ1bj6ImQQTFgoAQRYhBBgw
+z5kZo7AK3zA6kBq1RYkzaHEBQJnqTgYAhsDBQkFpCJ4BQsJCAcCAiICBhUKCQgL
AgQWAgMBAh4HAheAAAoJEEBq1RYkzaHEaVMBAJZ7Zdwy+Gri7rXNWdV705fmXBxX
6kee5HjJaeMaXT8CAQDaOm2kfxTbMq9yZMWpVIQRWzvIXSGr4SIqV3Izgpr/C7g4
BGepOBgSCisGAQQBl1UBBQEBB0Af3gTjId6GXPrd/kencNMq1R1MIbEmyD8la6he
Zn3xFAMBCAeIfgQYFgoAJhYhBBgw+z5kZo7AK3zA6kBq1RYkzaHEBQJnqTgYAhsM
BQkFpCJ4AAoJEEBq1RYkzaHEZmIBAPgfGlqLeR20pWVxefuJB9oeloBreP3BVEhY
8OmKIP8DAP9KjzUlLtXL0sjE1XKIcUTXwLJGLhm1m1ebxchhbOgGAg==
=V0uk
-----END PGP PUBLIC KEY BLOCK-----

```

PGP Fingerprint: 1830FB3E64668EC02B7CC0EA406AD51624CDA1C4

Note: You can encrypt your security reports using our PGP key.
If you have your own PGP key, we can send our response to you encrypted as well.

## Acknowledgments

We would like to thank the following individuals for their responsible disclosure of security vulnerabilities:

-  [List will be updated as contributions are made]
```
