# Contributing to MyOnlineRadio Scraper

Thank you for considering contributing to this project! 

## How to Contribute

### Reporting Issues
- Check if the issue already exists
- Provide clear steps to reproduce
- Include your Python version, OS, and relevant error messages
- Mention which channel(s) you were scraping

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and why it would be useful
- Consider implementation complexity

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly with multiple channels
5. Update documentation if needed
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/SWR4-Scrape.git
cd SWR4-Scrape

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if any)
pip install pytest black flake8
```

## Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and single-purpose
- Add type hints where appropriate

## Testing
- Test with at least 3 different channels
- Test both scraping and downloading
- Test error scenarios (invalid channels, unavailable videos)
- Verify ID3 tags are correctly embedded

## Areas for Contribution
- [ ] Add support for more radio channels
- [ ] Improve error handling
- [ ] Add more audio format options
- [ ] Optimize download speed
- [ ] Add album art embedding
- [ ] Create automated tests
- [ ] Improve documentation
- [ ] Add localization support

## Legal Considerations
- Ensure contributions respect copyright laws
- Don't include code that violates Terms of Service
- Add appropriate attribution for external code
- Follow GPL-3.0 license requirements

## Questions?
Feel free to open an issue for questions or discussion!

## Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

Thank you for contributing! 🎵
