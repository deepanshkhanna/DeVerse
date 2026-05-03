# DevVerse: Empathy-Driven Code Review & Onboarding Simulator

An AI-powered code review system that transforms technical feedback into empathetic, constructive guidance using IBM watsonx.ai and watsonx Orchestrate.

## 🎯 Overview

DevVerse bridges the gap between technical accuracy and human empathy in code reviews. It analyzes code using IBM Bob, transforms feedback through watsonx.ai's Granite models, and delivers personalized reviews via watsonx Orchestrate.

## 🏗️ Technical Architecture

### Zero-Trust AI Code Reviews with Trusted Execution Environment (TEE)

```
Developer → IBM Bob → [TEE: Hyper Protect] → watsonx.ai → watsonx Orchestrate → Slack/Teams
                            ↓
                    Secure In-Memory Processing
                    (Code never touches disk)
```

**Architecture Flow:**
1. **Code Analysis**: IBM Bob analyzes developer code and generates technical feedback
2. **TEE Secure Processing**: Python transformation script runs inside IBM Cloud Hyper Protect Virtual Server (Confidential Computing TEE)
   - Source code is loaded into encrypted memory
   - Formatting and prompt engineering occurs in isolated, hardware-encrypted environment
   - Zero persistence - code never written to disk or logs
3. **AI Transformation**: Formatted prompts sent to watsonx.ai Granite models for empathetic rewriting
4. **Delivery**: watsonx Orchestrate delivers personalized feedback via Slack/Teams

### 🛡️ Security Value Proposition

**Enterprise-Grade Confidential Computing for Proprietary Code:**

- **In-Memory Encryption**: Your source code is processed entirely within a hardware-based Trusted Execution Environment (TEE) using IBM Cloud Hyper Protect Virtual Servers. Code remains encrypted in memory and is never persisted to disk, logs, or external storage.

- **Zero-Trust AI Integration**: The TEE acts as a secure middle-layer that formats proprietary code for AI analysis without exposing raw source to watsonx.ai. Only sanitized, context-aware prompts leave the secure enclave, protecting intellectual property while leveraging AI capabilities.

- **Attestation & Compliance**: IBM Hyper Protect provides cryptographic attestation that code processing occurs only in verified, tamper-proof environments. Meets regulatory requirements for handling sensitive codebases in financial services, healthcare, and government sectors.

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- IBM Cloud account with watsonx.ai access
- watsonx Orchestrate workspace
- (Optional) Slack workspace for notifications

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/devverse.git
   cd devverse
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your IBM credentials
   ```

4. **Validate setup:**
   ```bash
   npm run validate-env
   ```

5. **Start development server:**
   ```bash
   npm run dev
   ```

## 📋 Configuration

See [`PHASE_1_SETUP_GUIDE.md`](./PHASE_1_SETUP_GUIDE.md) for detailed setup instructions.

### Required Environment Variables

- `WATSONX_API_KEY` - IBM Cloud API key
- `WATSONX_PROJECT_ID` - watsonx.ai project ID
- `WATSONX_REGION_URL` - API endpoint URL
- `ORCHESTRATE_WEBHOOK_URL` - Orchestrate workflow trigger URL

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run integration tests
npm run test:integration

# Generate coverage report
npm test -- --coverage
```

## 📚 Documentation

- [`PHASE_1_SETUP_GUIDE.md`](./PHASE_1_SETUP_GUIDE.md) - Environment setup
- [`DevVerse_Technical_Blueprint.md`](./DevVerse_Technical_Blueprint.md) - Architecture details
- [`docs/architecture.md`](./docs/architecture.md) - System design
- [`docs/api-reference.md`](./docs/api-reference.md) - API documentation

## 🔒 Security

- Never commit `.env` files
- Rotate API keys if exposed
- Use `.bobignore` to protect secrets from AI context
- Follow principle of least privilege for API keys

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

## 📄 License

MIT License - see LICENSE file for details

## 🏆 Hackathon

Built for IBM Bob Dev Day Hackathon 2026