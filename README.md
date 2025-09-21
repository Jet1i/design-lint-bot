# Design Lint Bot

An automated design specification checking tool that compares Figma design tokens with actual code implementation to ensure development teams follow design standards.

## 🚀 Features

- **Design Specification Checking**: Automatically compares Figma design tokens with CSS/HTML implementation
- **Multi-source Support**: Supports fetching code from GitHub repositories or local files
- **Smart Matching**: Supports intelligent matching of various design properties including colors, fonts, and spacing
- **Slack Integration**: Quick component compliance checking through Slack commands
- **Detailed Reports**: Generates detailed difference reports and compliance scores
- **Tolerance Handling**: Supports numerical tolerance and font inclusion matching

## 📁 Project Structure

```
design-lint-bot/
├── api/                    # FastAPI backend service
│   └── main.py            # Main API service
├── core/                   # Core functionality modules
│   ├── differ.py          # Design specification comparison logic
│   ├── parser_css.py      # CSS parser
│   ├── parser_html.py     # HTML parser
│   └── utils.py           # Utility functions
├── configs/                # Configuration files
│   ├── mapping.json       # Design token to CSS property mapping
│   └── mock_figma_tokens/ # Design tokens examples
├── integrations/           # Third-party integrations
│   └── github_client.py   # GitHub API client
├── slack/                  # Slack integration
│   └── app.py             # Slack Bot application
├── samples/                # Example files
│   └── button/            # Button component example
└── storage/                # Storage directory
    └── artifacts/         # Check results archive
```

## 🛠️ Installation and Configuration

### 1. Clone the Repository

```bash
git clone <repository-url>
cd design-lint-bot
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn python-dotenv requests beautifulsoup4 cssutils slack-bolt
```

### 3. Environment Configuration

Create a `.env` file and configure the following environment variables:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your-username/your-repo
GITHUB_DEFAULT_BRANCH=main

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_LEVEL_TOKEN=xapp-your-app-level-token

# API Configuration
CHECK_API_URL=http://localhost:8000/check
```

### 4. Start Services

#### Start API Service
```bash
cd api
uvicorn main:app --reload --port 8000
```

#### Start Slack Bot
```bash
cd slack
python app.py
```

## 📖 Usage

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Component Check
```bash
POST /check
Content-Type: application/json

{
  "component": "button",
  "branch": "main",
  "source": "auto"
}
```

**Parameters:**
- `component`: Component name (required)
- `branch`: Git branch name (optional, defaults to configured default branch)
- `source`: Data source (optional, auto/github/local)

### Slack Commands

Use the following commands in Slack:

```
/component button
/component button main
```

## 🔧 Configuration

### Design Token Mapping

Configure the mapping between design tokens and CSS properties in `configs/mapping.json`:

```json
{
  "color.background": ["background-color"],
  "color.text": ["color"],
  "color.border": ["border-color"],
  "color.hoverBackground": [".:hover.background-color"],
  "typography.fontFamily": ["font-family"],
  "typography.fontSize": ["font-size"],
  "typography.fontWeight": ["font-weight"],
  "typography.lineHeight": ["line-height"],
  "typography.letterSpacing": ["letter-spacing"],
  "spacing.paddingTop": ["padding-top", "padding"],
  "spacing.paddingRight": ["padding-right", "padding"],
  "spacing.paddingBottom": ["padding-bottom", "padding"],
  "spacing.paddingLeft": ["padding-left", "padding"],
  "spacing.borderRadius": ["border-radius"]
}
```

### Design Tokens Format

Design tokens files should follow this format (refer to `configs/mock_figma_tokens/button.json`):

```json
{
  "component": "button/primary",
  "tokens": {
    "color": {
      "background": "#0D6EFD",
      "text": "#FFFFFF",
      "border": "#0D6EFD",
      "hoverBackground": "#0B5ED7"
    },
    "typography": {
      "fontFamily": "Inter",
      "fontSize": 14,
      "fontWeight": 600,
      "lineHeight": 20,
      "letterSpacing": 0
    },
    "spacing": {
      "paddingTop": 8,
      "paddingRight": 12,
      "paddingBottom": 8,
      "paddingLeft": 12,
      "borderRadius": 6
    }
  }
}
```

## 🎯 Checking Rules

### Color Matching
- Supports HEX, RGB, RGBA formats
- Automatic normalization comparison (e.g., `#fff` and `#ffffff` are considered identical)

### Font Matching
- Supports font family inclusion matching
- Code containing the design font is sufficient to pass

### Numeric Matching
- Supports numerical tolerance (±1px)
- Automatic handling of `px` unit conversion

### Spacing Handling
- Intelligent parsing of CSS padding shorthand
- Supports 1-4 value padding syntax

## 📊 Output Format

Check results include the following information:

```json
{
  "summary": {
    "passed": 10,
    "failed": 2,
    "warnings": 0,
    "score": 0.83
  },
  "diffs": [
    {
      "token": "color.background",
      "design": "#0D6EFD",
      "code": "#0D6EFD",
      "match": true,
      "severity": null
    }
  ],
  "component": "button",
  "artifacts": {
    "source": "github",
    "branch": "main",
    "mainSelector": ".btn-primary"
  },
  "generatedAt": "2024-01-01T12:00:00Z"
}
```

## 🔍 Example

### Checking a Button Component

1. Ensure you have the corresponding design tokens file: `configs/mock_figma_tokens/button.json`
2. Ensure you have the corresponding code files:
   - GitHub: `src/components/button/button.css` and `src/components/button/button.html`
   - Local: `samples/button/button.css` and `samples/button/button.html`
3. Call the check API or use Slack commands

## 🤝 Contributing

Issues and Pull Requests are welcome to improve this project!

## 📄 License

MIT License
