# 📚 Documentation

Welcome to the Caja Backend documentation! This directory contains all the guides and references you need for development.

## 📖 Available Documents

### 🚀 Getting Started
- **[Development Guide](DEVELOPMENT.md)** - Comprehensive development setup and workflow guide
- **[Setup Summary](SETUP_SUMMARY.md)** - Complete overview of the custom environment setup

### �️ Development Tools
- **[Makefile Documentation](MAKEFILE.md)** - Complete guide to all 31 Make commands
- **[Commit Messages](COMMIT_MESSAGE.md)** - Suggested commit message formats

### �📋 Additional Resources
- **[Backend Setup Complete](BACKEND_SETUP_COMPLETE.md)** - Final reorganization summary
- **[Reorganization Complete](REORGANIZATION_COMPLETE.md)** - Project structure improvements

## 🔗 Quick Links

### For New Developers
1. Start with the main [README.md](../README.md) in the project root
2. Follow the [Development Guide](DEVELOPMENT.md) for detailed setup
3. Check the [Setup Summary](SETUP_SUMMARY.md) for overview

### For Existing Developers
- **Quick Start**: `cd backend && ./start-dev.sh`
- **Run Tests**: `cd backend && ./run-tests.sh`
- **Documentation**: See [Development Guide](DEVELOPMENT.md)

## 📁 Project Structure

```
conflicto/
├── backend/              # All backend code and scripts
│   ├── app/             # FastAPI application
│   ├── tests/           # Test suite
│   ├── Makefile         # Make commands
│   ├── setup.sh         # Environment setup
│   └── *.sh            # Development scripts
├── docs/                # This documentation directory
└── README.md           # Project overview
```

## 🤝 Contributing to Documentation

When adding new documentation:
1. Place it in this `docs/` directory
2. Update this index file
3. Link from the main README.md if relevant
4. Use clear, descriptive filenames

---

**Need help?** Start with the [Development Guide](DEVELOPMENT.md) or ask the team!