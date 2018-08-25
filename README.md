# telegram-pm-bot
concatnate your conversation between the bot and the sender.

based on [telegram-pm-chat-bot](https://github.com/Netrvin/telegram-pm-chat-bot).


## Installation
firstly prepared the following:
- python 3
- pip

then run :
```bash
pip install python-telegram-bot --upgrade
```


## Config
modify those on `/config.json` :
```c
{
    "Admin": 0,       // ID of admin account (number id)
    "Token": "",      // Token of bot
    "Lang": "en"      // name of the lang file
}
```


## Start
```bash
python main.py
```


## Directive
| command         | function                                   | parameter                                  |
| :---            | :---                                       | :---                                       |
| say             | start conversation                         | /say                                       |
| done            | end conversation                           | /done                                      |
| receipt_switch  | enable or disable receipt                  | /receipt_switch                            |
| markdown        | enable  markdown  (admin only)             | /markdown                                  |
| unmarkdown      | disable markdown  (admin only)             | /unmarkdown                                |
| messege_info    | info of the messege you point (admin only) | /messege_info                              |
| version         | version of bot                             | /version                                   |
