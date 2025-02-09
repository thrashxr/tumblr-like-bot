# Tumblr Auto Like Bot

A Python application that automatically likes content on Tumblr based on your specified tags.

## Features

-  🎯 Like content based on specific tags
-  ⏰ Customizable working hours
-  🔄 Hourly and daily like limits
-  📊 Detailed statistics and logging
-  ⚡ User-friendly graphical interface
-  🚫 Blog blocking system
-  📝 Content type filtering
-  🔒 Secure API usage

## Installation

1. Install required Python packages:

```bash
pip install -r requirements.txt
```

2. Create `.env` file and add your Tumblr API credentials:

```env
TUMBLR_CONSUMER_KEY='your_consumer_key'
TUMBLR_CONSUMER_SECRET='your_consumer_secret'
TUMBLR_OAUTH_TOKEN='your_oauth_token'
TUMBLR_OAUTH_SECRET='your_oauth_secret'
```

3. Configure the `config.yaml` file according to your needs.

## Usage

1. Start the program:

```bash
python src/gui.py
```

2. In the Settings menu:

   -  Add tags to like
   -  Select content types
   -  Set like limits
   -  Configure working hours

3. Click "Start" button to run the bot.

## Security

-  Keep your API keys secure
-  Never share your `.env` file
-  Keep daily and hourly limits at reasonable levels

## Contributing

1. Fork this repository
2. Create a new branch (`git checkout -b new-feature`)
3. Commit your changes (`git commit -am 'Added new feature'`)
4. Push to the branch (`git push origin new-feature`)
5. Create a Pull Request

## Davranış Kuralları / Code of Conduct

Bu proje [Katkıda Bulunanlar Sözleşmesi](CODE_OF_CONDUCT.md) davranış kurallarını benimsemiştir. Projeye katılarak bu kurallara uymayı kabul etmiş olursunuz.

This project has adopted the [Contributor Covenant](CODE_OF_CONDUCT.md) Code of Conduct. By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
