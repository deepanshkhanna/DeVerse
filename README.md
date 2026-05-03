# DevVerse: Empathy-Driven Code Review & Onboarding Simulator

An AI-powered code review system that transforms technical feedback into empathetic, constructive guidance using IBM watsonx.ai and watsonx Orchestrate.

## 🎯 Overview

DevVerse bridges the gap between technical accuracy and human empathy in code reviews. It analyzes code using IBM Bob, transforms feedback through watsonx.ai's Granite models, and delivers personalized reviews via watsonx Orchestrate.

## 🏗️ Architecture

```
Developer → IBM Bob → watsonx.ai → watsonx Orchestrate → Slack/Teams
```

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