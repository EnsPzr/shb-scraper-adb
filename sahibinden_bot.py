#!/usr/bin/env python3
"""
Sahibinden Mobilden Otomasyonu
Bu script ADB kullanarak Android cihaza bağlanır ve Sahibinden uygulamasını açar.
"""

import sys
from bot import SahibindenBot


def main():
    """Ana giriş noktası"""
    bot = SahibindenBot()
    success = bot.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

