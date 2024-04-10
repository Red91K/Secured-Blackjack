# Secured-Blackjack
- Blackjack game in python with basic security &amp; logging functionalities.
- Not intended to be a completely secure system, inherent limitations exist because it is run locally
- Check out the Obfuscated version that provides slightly more security (albeit mostly by obscurity)

Features:
- logs every transaction
- user account creation & authentication
- userdata file integrity monitoring
- hashing & salting of user credentials
- various anti-tampering measures

# Getting Started
```
git clone https://github.com/Red91K/Secured-Blackjack.git
cd Secured-Blackjack
python3 blackjack.py
```
choose option 1 (sign in) to create a new user account

# Viewing security & userdata logs
```
python3 audit.py
```
