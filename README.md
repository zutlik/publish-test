# Script URL Generator - Home Assistant Addon

Generate temporary, internet-accessible URLs to trigger your Home Assistant scripts from anywhere in the world. Perfect for chatbots, NFC tags, dashboards, and external integrations.

## 🚀 Features

- **Simple & Secure**: Generate cryptographically secure, temporary URLs
- **No Authentication Required**: The token itself is the gatekeeper
- **Single-Use URLs**: Each URL can only be used once
- **Automatic Expiration**: URLs expire after 10 minutes (configurable)
- **Beautiful UI**: Modern, responsive interface that matches Home Assistant
- **Internet Accessible**: Works with Nabu Casa, Cloudflare Tunnel, or any reverse proxy
- **Zero YAML**: No complex configuration required

## 📋 Requirements

- Home Assistant (Supervised or Core)
- Internet accessibility (Nabu Casa, Cloudflare Tunnel, etc.)
- Scripts configured in your Home Assistant instance

## 🛠️ Installation

### Method 1: Manual Installation (Recommended)

1. **Download the addon files** to your Home Assistant addons directory:
   ```bash
   cd /opt/addons
   git clone https://github.com/your-repo/script-url-generator.git
   ```

2. **Add the addon to Home Assistant**:
   - Go to **Settings** → **Add-ons** → **Add-on Store**
   - Click the three dots menu → **Repositories**
   - Add your local path: `/opt/addons/script-url-generator`

3. **Install and configure**:
   - Find "Script URL Generator" in your addon store
   - Click **Install**
   - Configure options (optional)
   - Click **Start**

### Method 2: Direct File Installation

1. Copy all files to a directory in your Home Assistant instance
2. Add the directory as a local addon repository
3. Install from the addon store

## ⚙️ Configuration

### Basic Configuration

The addon works out of the box with default settings:

- **Token Expiry**: 10 minutes
- **Max Tokens per Script**: 5
- **Logging**: Enabled

### Advanced Configuration

You can customize these settings in the addon configuration:

```yaml
token_expiry_minutes: 10      # How long URLs remain valid (1-1440 minutes)
max_tokens_per_script: 5      # Maximum active tokens per script (1-20)
enable_logging: true          # Log access attempts and events
```

## 🌐 Internet Accessibility Setup

### Option 1: Nabu Casa (Recommended)

If you have Home Assistant Cloud (Nabu Casa):

1. **Enable the addon** in Home Assistant
2. **Access via Nabu Casa**: The addon will be available at:
   ```
   https://your-instance.nabu.casa/script_url_generator
   ```
3. **Generated URLs** will be accessible via:
   ```
   https://your-instance.nabu.casa/script_url_generator/trigger/{token}
   ```

### Option 2: Cloudflare Tunnel

1. **Set up Cloudflare Tunnel** to your Home Assistant instance
2. **Configure the addon** to be accessible via your tunnel
3. **Generated URLs** will use your Cloudflare domain

### Option 3: Reverse Proxy (nginx, Traefik, etc.)

1. **Configure your reverse proxy** to forward requests to the addon
2. **Set up SSL certificates** for secure HTTPS access
3. **Update the addon configuration** if needed

## 📖 Usage

### Generating URLs

1. **Open the addon** in Home Assistant
2. **Select a script** from the dropdown
3. **Click "Generate URL"**
4. **Copy the generated URL** or use the copy button
5. **Use the URL anywhere** - it will trigger your script

### Using Generated URLs

- **Direct access**: Open the URL in any browser
- **HTTP requests**: Use with curl, wget, or any HTTP client
- **External services**: Integrate with chatbots, IFTTT, Zapier, etc.
- **NFC tags**: Program NFC tags with the URL
- **QR codes**: Generate QR codes for easy access

### Example Usage

```bash
# Trigger a script via curl
curl "https://your-instance.nabu.casa/script_url_generator/trigger/abc123..."

# Use with IFTTT Webhook
# URL: https://your-instance.nabu.casa/script_url_generator/trigger/abc123...
# Method: GET
```

## 🔒 Security Features

### Token Security

- **Cryptographically Secure**: Uses `secrets.token_urlsafe(32)` for token generation
- **Unguessable**: 256-bit random tokens (43 characters)
- **Single-Use**: Each token can only trigger the script once
- **Time-Limited**: Tokens expire after configurable duration
- **Automatic Cleanup**: Expired tokens are automatically removed

### Access Control

- **No Authentication Required**: The token itself provides access
- **Script-Specific**: Each token is tied to a specific script
- **Rate Limiting**: Configurable limit on tokens per script
- **Logging**: Optional logging of all access attempts

### Best Practices

1. **Keep URLs Private**: Don't share generated URLs publicly
2. **Monitor Usage**: Check logs for unexpected access
3. **Regular Rotation**: Generate new URLs as needed
4. **Secure Network**: Use HTTPS for all external access

## 🐛 Troubleshooting

### Common Issues

#### "Script not found" Error
- **Cause**: Script was deleted or renamed
- **Solution**: Generate a new URL for the updated script

#### "Token expired" Error
- **Cause**: URL was accessed after expiration time
- **Solution**: Generate a new URL

#### "Token already used" Error
- **Cause**: URL was accessed multiple times
- **Solution**: Generate a new URL

#### Addon won't start
- **Check logs**: Look at the addon logs in Home Assistant
- **Verify permissions**: Ensure the addon has API access
- **Check configuration**: Validate the config.yaml file

#### URLs not accessible from internet
- **Verify Nabu Casa**: Ensure Home Assistant Cloud is enabled
- **Check firewall**: Ensure port 8123 is accessible
- **Test locally**: Verify the addon works within your network

### Debugging

#### Enable Debug Logging

Add to your addon configuration:
```yaml
enable_logging: true
```

#### Check Active Tokens

Access the debug endpoint:
```
GET /api/tokens
```

#### Health Check

Verify the addon is running:
```
GET /health
```

## 🔧 API Reference

### Endpoints

#### Generate URL
```
POST /api/generate
Content-Type: application/json

{
  "script_id": "script.your_script_name"
}
```

**Response:**
```json
{
  "token": "abc123...",
  "url": "https://your-instance.nabu.casa/script_url_generator/trigger/abc123...",
  "expires_at": "2024-01-01T12:00:00",
  "expires_in_minutes": 10
}
```

#### Trigger Script
```
GET /trigger/{token}
```

**Response:** HTML page showing success or error

#### List Scripts
```
GET /api/scripts
```

**Response:**
```json
[
  {
    "entity_id": "script.your_script",
    "name": "Your Script Name"
  }
]
```

#### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🚀 Advanced Features

### Future Enhancements

- **Script Arguments**: Support for passing parameters to scripts
- **Multiple Uses**: Configurable use count per token
- **Token Revocation**: Cancel tokens before expiration
- **Dashboard Integration**: Custom Lovelace card
- **Webhook Support**: Direct webhook endpoints
- **Analytics**: Usage statistics and monitoring

### Custom Integrations

#### IFTTT Integration
1. Create an IFTTT applet
2. Use "Webhooks" as the trigger
3. Set the URL to your generated script URL
4. Configure your desired trigger conditions

#### Google Home Integration
1. Use IFTTT to connect Google Home to webhooks
2. Set up voice commands to trigger your scripts
3. Use the generated URLs as webhook endpoints

#### NFC Tags
1. Program NFC tags with generated URLs
2. Tap the tag to trigger your script
3. Generate new URLs periodically for security

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run locally**: `python main.py`
4. **Test changes**: Access `http://localhost:8080`

### Testing

- **Unit tests**: Run with pytest
- **Integration tests**: Test with actual Home Assistant instance
- **Security tests**: Verify token generation and validation

## 📞 Support

- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check this README and inline code comments

## 🙏 Acknowledgments

- Home Assistant community for inspiration
- FastAPI for the excellent web framework
- Font Awesome for the beautiful icons

---

**Happy automating! 🏠✨** 